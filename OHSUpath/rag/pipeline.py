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


def _pair_from_cfg(weights_obj: Any, default_sparse: float, default_dense: float) -> tuple[float, float]:
    """
    Support both dataclass (fields: sparse/dense) and dict (keys: sparse/dense).
    """
    s = _cfg_get(weights_obj, "sparse", default_sparse)
    d = _cfg_get(weights_obj, "dense", default_dense)
    try:
        return float(s), float(d)
    except Exception:
        return float(default_sparse), float(default_dense)


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
                source_keys=tuple(_cfg_get(split, "source_keys", ["source", "file_path", "path"]))[0:],
                page_keys=tuple(_cfg_get(split, "page_keys", ["page", "page_number", "page_no"]))[0:],
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
                print(
                    "[WARN] FAISS metric=ip but both embedding.normalize_embeddings and "
                    "faiss.normalize_query_in_ip are false; results may degrade."
                )

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
        # Keep dense-only retriever as fallback
        retr = _cfg_get(self.cfg, "retriever", None)
        faiss_cfg = _cfg_get(self.cfg, "faiss", None)
        emb_cfg = _cfg_get(self.cfg, "embedding", None)
        retrieval_cfg = _cfg_get(self.cfg, "retrieval", None)
        mode = str(_cfg_get(retrieval_cfg, "mode", "dense")).lower()

        # ---- dense retriever (current logic) ----
        k = int(_cfg_get(retr, "k", 4))
        fetch_k = int(_cfg_get(retr, "fetch_k", 50))
        skw = dict(_cfg_get(retr, "search_kwargs", {}) or {})
        skw.setdefault("fetch_k", fetch_k)
        if _cfg_get(retr, "use_mmr", False):
            skw.setdefault("mmr", True)
            skw.setdefault("lambda_mult", float(_cfg_get(retr, "lambda_mult", 0.5)))
        st = _cfg_get(retr, "score_threshold", None)
        if st is not None:
            skw.setdefault("score_threshold", float(st))

        dense_lc_retriever = self.vindex.as_retriever(
            k=k,
            search_type=str(_cfg_get(retr, "search_type", "similarity")),
            embedding=self.embedder.embed,
            normalize_query_in_ip=bool(_cfg_get(faiss_cfg, "normalize_query_in_ip", True)),
            search_kwargs=skw,
        )

        # Dense-only: return directly
        if mode == "dense":
            return dense_lc_retriever

        # ---- prepare sparse index (bm25s default, silent fallback to rank_bm25) ----
        from .vectorstores.bm25_store import BM25SparseIndex
        from .retriever import HybridBM25FaissRetriever, QueryTypeDetector
        from .rerankers import CharNGramReranker, CharNGramCfg

        sparse_backend = str(_cfg_get(_cfg_get(self.cfg, "sparse", None), "backend", "bm25s")).lower()
        sparse_path = os.path.join(str(self.layout.index_dir), "sparse_index.pkl")

        def _collect_items_from_docstore():
            ds = getattr(self.vindex, "_docstore", None)
            dct = getattr(ds, "_dict", None) if ds is not None else None
            if not isinstance(dct, dict):
                return []
            items = []
            for cid, doc in dct.items():
                meta = getattr(doc, "metadata", {}) or {}
                src = meta.get("source") or meta.get("file_path") or meta.get("path") or ""
                page = meta.get("page") or meta.get("page_number") or meta.get("page_no") or ""
                txt = f"{doc.page_content}\n[SRC:{src} P:{page}]"
                items.append((cid, txt))
            return items

        # Load or build sparse index
        if os.path.exists(sparse_path):
            try:
                sparse_index = BM25SparseIndex.load(sparse_path)
            except Exception:
                items = _collect_items_from_docstore()
                sparse_index = BM25SparseIndex(backend=sparse_backend)
                sparse_index.build(items)
                sparse_index.save(sparse_path)
        else:
            items = _collect_items_from_docstore()
            sparse_index = BM25SparseIndex(backend=sparse_backend)
            sparse_index.build(items)
            sparse_index.save(sparse_path)

        def sparse_search(query: str, topk: int):
            return sparse_index.search(query, k=topk)

        # Direct dense search on FAISS (hybrid path does not use LC MMR)
        import numpy as np
        metric = str(_cfg_get(emb_cfg, "faiss_metric", "l2")).lower()
        norm_q_flag = bool(_cfg_get(faiss_cfg, "normalize_query_in_ip", True))

        def _embed_query_one(q: str):
            try:
                vec = self.embedder.embed([q])[0]
            except TypeError:
                vec = self.embedder.embed(q)
            v = np.asarray(vec, dtype=np.float32).reshape(1, -1)
            if metric == "ip" and norm_q_flag:
                n = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
                v = v / n
            return v

        def dense_search(query: str, topk: int):
            v = _embed_query_one(query)
            D, I = self.vindex._index.search(v, topk)
            idmap = self.vindex._id_map
            out = []
            if metric == "l2":
                for d, i in zip(D[0].tolist(), I[0].tolist()):
                    if i != -1:
                        # smaller distance is better -> take negative
                        out.append((idmap.get(i), -float(d)))
            else:  # ip
                for d, i in zip(D[0].tolist(), I[0].tolist()):
                    if i != -1:
                        out.append((idmap.get(i), float(d)))
            return [(cid, sc) for cid, sc in out if cid]

        # id -> Document map
        ds = getattr(self.vindex, "_docstore", None)
        dd = getattr(ds, "_dict", None) if ds is not None else {}
        def id2doc(cid: str):
            return dd[cid]
        def id2text(cid: str) -> str:
            return dd[cid].page_content

        # Detector + Reranker config (ngram: mode=auto)
        hybrid_cfg = _cfg_get(retrieval_cfg, "hybrid", None) or {}
        ngram_cfg = _cfg_get(_cfg_get(self.cfg, "sparse", None), "ngram_rerank", None) or {}

        # Read weights from dataclass or dict
        weights_cfg = _cfg_get(hybrid_cfg, "weights", None)
        kw_pair = _pair_from_cfg(_cfg_get(weights_cfg, "keyword", None), 0.8, 0.2)
        sem_pair = _pair_from_cfg(_cfg_get(weights_cfg, "semantic", None), 0.3, 0.7)

        detector = QueryTypeDetector(
            weights_keyword=kw_pair,
            weights_semantic=sem_pair,
            base_sparse_k=int(_cfg_get(hybrid_cfg, "sparse_k", 80)),
            base_dense_k=int(_cfg_get(hybrid_cfg, "dense_k", 40)),
        )

        rerank_mode = str(_cfg_get(ngram_cfg, "mode", "auto")).lower()  # auto | on | off
        reranker = None
        if rerank_mode in {"auto", "on"}:
            reranker = CharNGramReranker(CharNGramCfg(
                n=int(_cfg_get(ngram_cfg, "n", 3)),
                weight=float(_cfg_get(ngram_cfg, "weight", 0.35)),
                jaccard_w=float(_cfg_get(ngram_cfg, "jaccard_w", 0.6)),
                fuzz_w=float(_cfg_get(ngram_cfg, "fuzz_w", 0.4)),
            ))

        final_k = int(_cfg_get(hybrid_cfg, "final_k", 12))
        hybrid_retriever = HybridBM25FaissRetriever(
            sparse_search=sparse_search,
            dense_search=dense_search,
            id2doc=id2doc,
            id2text=id2text,
            detector=detector,
            reranker=reranker,
            rerank_mode=rerank_mode,
            auto_gap_threshold=float(_cfg_get(ngram_cfg, "gap_threshold", 0.05)),
            auto_top1_threshold=float(_cfg_get(ngram_cfg, "top1_threshold", 0.40)),
            auto_max_rerank=int(_cfg_get(ngram_cfg, "max_rerank", 120)),
            final_k=final_k,
        )

        # pure sparse mode: force (1.0, 0.0)
        if mode == "sparse":
            hybrid_retriever.detector = QueryTypeDetector(
                weights_keyword=(1.0, 0.0),
                weights_semantic=(1.0, 0.0),
                base_sparse_k=detector.ks,
                base_dense_k=0,
            )

        # For hybrid/auto, return hybrid retriever
        return hybrid_retriever

    # def build_qa(self):
    #     return build_qa(self.serve(), self.cfg)

    def build_qa(self):
        from .retriever import build_qa as _build_qa
        return _build_qa(self.serve(), self.cfg)
