# rag/pipeline.py

from __future__ import annotations
import os
from typing import Dict, Any, List
from config import load_config
from .storage.fs_paths import FsLayout, ensure_dirs
from .loaders.pdf_loader_opt import PdfLoaderOptimized, LoaderCfg
from .chunkers.rcts_chunker_parallel import RctsChunkerParallel, SplitCfg as SplitCfgChunker
from .embedders.st_multi_gpu import STMultiGPUEmbedder, STCfg
from .vectorstores.faiss_store import FaissIndex
from .index_manager import IndexManager
# from .retriever import build_qa


def _cfg_get(obj: Any, name: str, default: Any = None) -> Any:
    """Read config from either an object or a dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


class RagPipeline:
    def __init__(self, cfg: Any = None, *, yaml_path: str = "config.yaml", use_yaml: bool = True):
        """
        Assemble components using the global config.
        """
        if cfg is None:
            cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)
        self.cfg = cfg
        self._yaml_path = yaml_path
        self._use_yaml = use_yaml

        # ---- layout from cfg.paths ----
        paths = _cfg_get(self.cfg, "paths", None)
        self.layout = FsLayout.from_base(
            _cfg_get(paths, "store_dir", ".rag_store"),
            index_dirname=_cfg_get(paths, "index_dirname", "index"),
            manifest_filename=_cfg_get(paths, "manifest_filename", "manifest.sqlite"),
            embed_cache_filename=_cfg_get(paths, "embed_cache_filename", "embed_cache.sqlite"),
            journal_filename=_cfg_get(paths, "journal_filename", "journal.log"),
            lock_filename=_cfg_get(paths, "lock_filename", ".rag.lock"),
            tmp_dirname=_cfg_get(paths, "tmp_dirname", "_tmp"),
        )
        ensure_dirs(self.layout)

        # ---- loader (pdf_loader + paths) ----
        pdf_loader = _cfg_get(self.cfg, "pdf_loader", None)
        self.loader = PdfLoaderOptimized(
            LoaderCfg(
                exts=[e.lower() for e in (_cfg_get(paths, "allowed_extensions", [".pdf"]) or [".pdf"])],
                prefetch_budget_mb=int(_cfg_get(pdf_loader, "prefetch_budget_mb", 64)),
                io_batch_files=int(_cfg_get(pdf_loader, "io_batch_files", 8)),
                num_proc=_cfg_get(pdf_loader, "num_proc", "max"),
                pdf_text_mode=_cfg_get(paths, "pdf_text_mode", "text"),
            )
        )

        # ---- chunker (split + hashing) ----
        split = _cfg_get(self.cfg, "split", None)
        hashing = _cfg_get(self.cfg, "hashing", None)
        _chunker_nproc = 1 if os.name == "nt" else _cfg_get(split, "num_proc", "max")
        self.chunker = RctsChunkerParallel(
            SplitCfgChunker(
                chunk_size=int(_cfg_get(split, "chunk_size", 1200)),
                chunk_overlap=int(_cfg_get(split, "chunk_overlap", 200)),
                num_proc=_chunker_nproc,
                source_keys=tuple(_cfg_get(split, "source_keys", ["source", "file_path", "path"])),
                page_keys=tuple(_cfg_get(split, "page_keys", ["page", "page_number", "page_no"])),
                chunk_id_hash_len=int(_cfg_get(hashing, "chunk_id_hash_len", 32)),
            )
        )

        # ---- embedder ----
        emb = _cfg_get(self.cfg, "embedding", None)
        normalize_flag = _cfg_get(emb, "normalize_embeddings", _cfg_get(emb, "normalize", False))
        self.embedder = STMultiGPUEmbedder(
            STCfg(
                model_name=_cfg_get(emb, "model_name", "./models/all-MiniLM-L6-v2"),
                embedding_dim=int(_cfg_get(emb, "embedding_dim", 384)),
                batch_size=int(_cfg_get(emb, "batch_size", 64)),
                multi_gpu=_cfg_get(emb, "multi_gpu", False),
                normalize=bool(normalize_flag),
                dtype=str(_cfg_get(emb, "dtype", "float32")),
                pad_to_batch=bool(_cfg_get(emb, "pad_to_batch", False)),
                in_queue_maxsize=int(_cfg_get(emb, "in_queue_maxsize", 4)),
                allow_cpu_fallback=bool(_cfg_get(emb, "allow_cpu_fallback", True)),
            )
        )

        # ---- vector index (faiss) ----
        faiss_cfg = _cfg_get(self.cfg, "faiss", None)
        self.vindex = FaissIndex(
            embedding_dim=int(_cfg_get(emb, "embedding_dim", 384)),
            model_name=self.embedder.model_name,
            metric=str(_cfg_get(emb, "faiss_metric", "l2")),
            strict_meta_check=bool(_cfg_get(faiss_cfg, "strict_meta_check", True)),
            clear_on_delete=bool(_cfg_get(faiss_cfg, "clear_on_delete", True)),
        )

        metric = str(_cfg_get(emb, "faiss_metric", "l2")).lower()
        if metric == "ip":
            norm_emb = bool(_cfg_get(emb, "normalize_embeddings", False))
            norm_q = bool(_cfg_get(faiss_cfg, "normalize_query_in_ip", True))
            if not (norm_emb or norm_q):
                print("[WARN] FAISS metric=ip but both embedding.normalize_embeddings and "
                      "faiss.normalize_query_in_ip are false; results may degrade.")

        # ---- manager (orchestrator) ----
        self.manager = IndexManager(self.layout, self.vindex, self.embedder, self.loader, self.chunker, self.cfg)

    @classmethod
    def from_config(cls, *, yaml_path: str = "config.yaml", use_yaml: bool = True) -> "RagPipeline":
        return cls(None, yaml_path=yaml_path, use_yaml=use_yaml)

    def reload_config(self, *, yaml_path: str | None = None, use_yaml: bool | None = None) -> None:
        yp = yaml_path if yaml_path is not None else self._yaml_path
        uy = use_yaml if use_yaml is not None else self._use_yaml
        self.cfg = load_config(yaml_path=yp, use_yaml=uy)

    # ---------- Index lifecycle ----------
    def bootstrap(self):
        paths = _cfg_get(self.cfg, "paths", None)
        return self.manager.bootstrap(
            _cfg_get(paths, "data_dir", "minidata/LabDocs"),
            _cfg_get(paths, "allowed_extensions", [".pdf"]),
        )

    def refresh(self, prev_manifest, **kw):
        """
        Pass-through for extra controls like progress=callback.
        """
        paths = _cfg_get(self.cfg, "paths", None)
        return self.manager.refresh(
            _cfg_get(paths, "data_dir", "minidata/LabDocs"),
            _cfg_get(paths, "allowed_extensions", [".pdf"]),
            prev_manifest,
            **({k: v for k, v in kw.items() if k in ("progress",)})  # forward whitelisted kwargs
        )

    # ---------- Retrieval & QA ----------
    def serve(self):
        retr = _cfg_get(self.cfg, "retriever", None)
        faiss_cfg = _cfg_get(self.cfg, "faiss", None)

        k = int(_cfg_get(retr, "k", 4))
        fetch_k = int(_cfg_get(retr, "fetch_k", 50))

        # merge user-provided kwargs without duplicating "k"
        skw = dict(_cfg_get(retr, "search_kwargs", {}) or {})
        skw.setdefault("fetch_k", fetch_k)

        if _cfg_get(retr, "use_mmr", False):
            skw.setdefault("mmr", True)
            skw.setdefault("lambda_mult", float(_cfg_get(retr, "lambda_mult", 0.5)))

        st = _cfg_get(retr, "score_threshold", None)
        if st is not None:
            skw.setdefault("score_threshold", float(st))

        return self.vindex.as_retriever(
            k=k,
            search_type=str(_cfg_get(retr, "search_type", "similarity")),
            embedding=self.embedder.embed,
            normalize_query_in_ip=bool(_cfg_get(faiss_cfg, "normalize_query_in_ip", True)),
            search_kwargs=skw,
        )

    # def build_qa(self):
    #     return build_qa(self.serve(), self.cfg)

    def build_qa(self):
        from .retriever import build_qa as _build_qa
        return _build_qa(self.serve(), self.cfg)

