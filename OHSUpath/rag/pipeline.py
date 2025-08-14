# rag/pipeline.py

from __future__ import annotations

from typing import Dict, Any, List
from .storage.fs_paths import FsLayout, ensure_dirs
from .loaders.pdf_loader_opt import PdfLoaderOptimized, LoaderCfg
from .chunkers.rcts_chunker_parallel import RctsChunkerParallel, SplitCfg as SplitCfgChunker
from .embedders.st_multi_gpu import STMultiGPUEmbedder, STCfg
from .vectorstores.faiss_store import FaissIndex
from .index_manager import IndexManager
from .retriever import build_qa


class RagPipeline:
    def __init__(self, cfg):
        """
        Assemble components using the global config.
        """
        self.cfg = cfg

        # ---- layout from cfg.paths ----
        self.layout = FsLayout.from_base(
            cfg.paths.store_dir,
            index_dirname=cfg.paths.index_dirname,
            manifest_filename=cfg.paths.manifest_filename,
            embed_cache_filename=cfg.paths.embed_cache_filename,
            journal_filename=cfg.paths.journal_filename,
            lock_filename=cfg.paths.lock_filename,
            tmp_dirname=cfg.paths.tmp_dirname,
        )
        ensure_dirs(self.layout)

        # ---- loader (pdf_loader + paths) ----
        self.loader = PdfLoaderOptimized(
            LoaderCfg(
                exts=[e.lower() for e in (cfg.paths.allowed_extensions or [".pdf"])],
                prefetch_budget_mb=int(cfg.pdf_loader.prefetch_budget_mb),
                io_batch_files=int(cfg.pdf_loader.io_batch_files),
                num_proc=cfg.pdf_loader.num_proc if cfg.pdf_loader.num_proc is not None else "max",
                pdf_text_mode=cfg.paths.pdf_text_mode,
            )
        )

        # ---- chunker (split + hashing) ----
        self.chunker = RctsChunkerParallel(
            SplitCfgChunker(
                chunk_size=int(cfg.split.chunk_size),
                chunk_overlap=int(cfg.split.chunk_overlap),
                num_proc=cfg.split.num_proc,
                source_keys=tuple(cfg.split.source_keys),
                page_keys=tuple(cfg.split.page_keys),
                # ensure chunk_id stability matches global hashing policy
                chunk_id_hash_len=int(cfg.hashing.chunk_id_hash_len),
            )
        )

        # ---- embedder ----
        self.embedder = STMultiGPUEmbedder(
            STCfg(
                model_name=cfg.embedding.model_name,
                embedding_dim=int(cfg.embedding.embedding_dim),
                batch_size=int(cfg.embedding.batch_size),
                multi_gpu=cfg.embedding.multi_gpu,
                normalize=bool(cfg.embedding.normalize_embeddings),
                dtype=str(cfg.embedding.dtype),
                pad_to_batch=bool(cfg.embedding.pad_to_batch),
                in_queue_maxsize=int(cfg.embedding.in_queue_maxsize),
            )
        )

        # ---- vector index (faiss) ----
        self.vindex = FaissIndex(
            embedding_dim=int(cfg.embedding.embedding_dim),
            model_name=self.embedder.model_name,
            metric=str(cfg.embedding.faiss_metric),
            strict_meta_check=bool(cfg.faiss.strict_meta_check),
            clear_on_delete=bool(cfg.faiss.clear_on_delete),
        )

        # ---- manager (orchestrator) ----
        self.manager = IndexManager(self.layout, self.vindex, self.embedder, self.loader, self.chunker, cfg)

    # ---------- Index lifecycle ----------

    def bootstrap(self):
        return self.manager.bootstrap(self.cfg.paths.data_dir, self.cfg.paths.allowed_extensions)

    def refresh(self, prev_manifest):
        return self.manager.refresh(self.cfg.paths.data_dir, self.cfg.paths.allowed_extensions, prev_manifest)

    # ---------- Retrieval & QA ----------

    def serve(self):
        """
        Build a retriever backed by FAISS. MUST pass embedding (callable) here.
        """
        return self.vindex.as_retriever(
            k=int(self.cfg.retriever.k),
            search_type=str(self.cfg.retriever.search_type),
            embedding=self.embedder.embed,  # callable(texts|text)->vectors
            normalize_query_in_ip=bool(self.cfg.faiss.normalize_query_in_ip),
            search_kwargs={"k": int(self.cfg.retriever.k), "fetch_k": int(self.cfg.retriever.fetch_k)},
        )

    def build_qa(self):
        return build_qa(self.serve(), self.cfg)


