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
            _cfg_get(paths, "data_dir", "data"),
            _cfg_get(paths, "allowed_extensions", [".pdf"]),
        )

    def refresh(self, prev_manifest, **kw):
        """
        Pass-through for extra controls like progress=callback.
        """
        paths = _cfg_get(self.cfg, "paths", None)
        return self.manager.refresh(
            _cfg_get(paths, "data_dir", "data"),
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

        # ---- sparse shards (base + delta) ----
        from .vectorstores.bm25_shards import BM25ShardSet
        from .retriever import HybridBM25FaissRetriever, QueryTypeDetector
        from .rerankers import CharNGramReranker, CharNGramCfg

        sparse_backend = str(_cfg_get(_cfg_get(self.cfg, "sparse", None), "backend", "bm25s")).lower()
        shards_root = os.path.join(str(self.layout.index_dir), "sparse_shards")

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

        shardset = BM25ShardSet(shards_root, backend=sparse_backend)
        shardset.ensure_base(_collect_items_from_docstore)

        def sparse_search(query: str, topk: int):
            ds = getattr(self.vindex, "_docstore", None)
            exists = set(getattr(ds, "_dict", {}).keys()) if ds is not None else set()
            pairs = shardset.search(query, k=topk)
            return [(cid, sc) for cid, sc in pairs if cid in exists]

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

    # ---------- LLM Prompt Building & Direct Call ----------
    def get_doc_total_pages(self, source_path: str) -> int | None:
        """
        Get total number of pages for a PDF from the docstore metadata.
        Returns None if not found.
        """
        ds = getattr(self.vindex, "_docstore", None)
        if ds is None:
            return None
        dct = getattr(ds, "_dict", None)
        if not isinstance(dct, dict):
            return None

        # Find any document from this source and check metadata
        for doc in dct.values():
            meta = getattr(doc, "metadata", {}) or {}
            src = meta.get("source") or meta.get("file_path") or meta.get("path") or ""
            if src == source_path:
                # Check for total_pages in metadata
                total = meta.get("total_pages") or meta.get("num_pages")
                if total is not None:
                    try:
                        return int(total)
                    except (ValueError, TypeError):
                        pass
        return None

    def get_page_doc(self, source_path: str, page: int) -> Any | None:
        """
        Get a document for a specific page from the docstore.
        Returns None if not found.
        """
        ds = getattr(self.vindex, "_docstore", None)
        if ds is None:
            return None
        dct = getattr(ds, "_dict", None)
        if not isinstance(dct, dict):
            return None

        # Find document matching source and page
        for doc in dct.values():
            meta = getattr(doc, "metadata", {}) or {}
            src = meta.get("source") or meta.get("file_path") or meta.get("path") or ""
            pg = meta.get("page") or meta.get("page_number") or meta.get("page_no")
            if src == source_path and pg is not None:
                try:
                    if int(pg) == page:
                        return doc
                except (ValueError, TypeError):
                    pass
        return None

    def build_prompt(
        self,
        question: str,
        top_docs: List[Any],
        max_chars: int = 80_000,
    ) -> tuple[str, List[Any], Dict[str, Dict]]:
        """
        Build a structured prompt with:
        - User question
        - Top-5 retrieved chunks (with metadata)
        - Supplemental context (neighbor pages or full short PDFs)

        Returns:
            prompt_text: str - the formatted prompt
            used_docs: List[Document] - all documents used (chunks + supplemental)
            index_map: Dict[str, Dict] - ChunkID -> metadata mapping
        """
        # Limit to top 5
        top_5 = top_docs[:5]

        # Build index map and gather unique sources
        index_map = {}
        source_pages = {}  # source -> set of page numbers

        for i, doc in enumerate(top_5, 1):
            meta = getattr(doc, "metadata", {}) or {}
            source = meta.get("source") or meta.get("file_path") or meta.get("path") or ""
            page = meta.get("page") or meta.get("page_number") or meta.get("page_no")
            chunk_id = meta.get("chunk_id") or f"chunk_{i}"

            # Extract filename from source path
            filename = os.path.basename(source) if source else "unknown"

            index_map[chunk_id] = {
                "source": source,
                "page": page,
                "filename": filename,
                "index": i,
            }

            # Track pages per source
            if source:
                if source not in source_pages:
                    source_pages[source] = set()
                if page is not None:
                    try:
                        source_pages[source].add(int(page))
                    except (ValueError, TypeError):
                        pass

        # Start building prompt
        prompt_parts = []
        prompt_parts.append("# Task")
        prompt_parts.append("You are a domain assistant. Use the **Sources** to answer the **User Question** accurately.")
        prompt_parts.append("- Prefer facts from the sources. If uncertain, say so.")
        prompt_parts.append("- Put your chain-of-thought in a `<think>...</think>` block first. Then write the final answer under **Answer**.")
        prompt_parts.append("- Cite evidence inline like [S1], [S2: p.5] using the IDs in **Sources**.")
        prompt_parts.append("- Keep the final answer concise and structured.")
        prompt_parts.append("")
        prompt_parts.append("## User Question")
        prompt_parts.append(question)
        prompt_parts.append("")
        prompt_parts.append("## Sources (Top-5 Retrieved Chunks)")

        # Helper to convert absolute path to relative path
        def make_relative_path(abs_path: str) -> str:
            """Convert absolute path to relative path from data directory."""
            if not abs_path or abs_path == "unknown":
                return abs_path
            # Try to find 'data/' in the path and make it relative from there
            if "/data/" in abs_path:
                parts = abs_path.split("/data/")
                return parts[-1] if len(parts) > 1 else abs_path
            # Fallback: just return basename if no data dir found
            return os.path.basename(abs_path)

        # Add top 5 chunks
        chunk_texts = []
        for i, doc in enumerate(top_5, 1):
            meta = getattr(doc, "metadata", {}) or {}
            source = meta.get("source") or meta.get("file_path") or meta.get("path") or "unknown"
            page = meta.get("page") or meta.get("page_number") or meta.get("page_no") or "?"
            filename = os.path.basename(source) if source else "unknown"
            relative_path = make_relative_path(source)
            text = doc.page_content or ""

            chunk_texts.append((
                f"[S{i}] file: {filename} | path: {relative_path} | page: {page}",
                "---",
                text,
                ""
            ))

        # Gather supplemental pages
        supplemental_docs = []
        supplemental_texts = []
        next_id = len(top_5) + 1

        for source, pages in source_pages.items():
            if not source:
                continue

            total_pages = self.get_doc_total_pages(source)
            filename = os.path.basename(source)

            selected_pages = []

            if total_pages and total_pages <= 3:
                # Include all pages
                selected_pages = list(range(1, total_pages + 1))
            else:
                # Include hit page ± 1
                for hit_page in pages:
                    for offset in [-1, 0, 1]:
                        pg = hit_page + offset
                        if total_pages:
                            if 1 <= pg <= total_pages and pg not in selected_pages:
                                selected_pages.append(pg)
                        elif pg >= 1 and pg not in selected_pages:
                            selected_pages.append(pg)
                selected_pages.sort()

            # Fetch page documents
            for pg in selected_pages:
                # Skip if already in top_5
                skip = False
                for doc in top_5:
                    m = getattr(doc, "metadata", {}) or {}
                    s = m.get("source") or m.get("file_path") or m.get("path") or ""
                    p = m.get("page") or m.get("page_number") or m.get("page_no")
                    try:
                        if s == source and p is not None and int(p) == pg:
                            skip = True
                            break
                    except (ValueError, TypeError):
                        pass

                if not skip:
                    page_doc = self.get_page_doc(source, pg)
                    if page_doc:
                        supplemental_docs.append(page_doc)
                        text = page_doc.page_content or ""
                        relative_path = make_relative_path(source)
                        supplemental_texts.append((
                            f"[S{next_id}] file: {filename} | path: {relative_path} | page: {pg}",
                            "---",
                            text,
                            ""
                        ))
                        next_id += 1

        # Estimate current size
        def estimate_size(parts_list):
            return sum(sum(len(s) for s in part) for part in parts_list)

        header_size = len("\n".join(prompt_parts))
        chunk_size = estimate_size(chunk_texts)
        supp_size = estimate_size(supplemental_texts)
        footer_size = len("\n## Answer\n\n")

        total_size = header_size + chunk_size + supp_size + footer_size

        # Truncation if needed
        if total_size > max_chars:
            # print(f"[PROMPT] Truncating: current={total_size}, max={max_chars}")
            pass

            # Truncate supplemental first
            char_per_page = 4000
            for i, (header, sep, text, blank) in enumerate(supplemental_texts):
                if len(text) > char_per_page:
                    truncated = text[:char_per_page] + "\n[...truncated]"
                    supplemental_texts[i] = (header, sep, truncated, blank)

            supp_size = estimate_size(supplemental_texts)
            total_size = header_size + chunk_size + supp_size + footer_size

            # If still over, truncate chunks
            if total_size > max_chars:
                min_chunk_size = 1500
                for i, (header, sep, text, blank) in enumerate(chunk_texts):
                    if len(text) > min_chunk_size:
                        truncated = text[:min_chunk_size] + "\n[...truncated]"
                        chunk_texts[i] = (header, sep, truncated, blank)

        # Assemble final prompt
        for header, sep, text, blank in chunk_texts:
            prompt_parts.append(header)
            prompt_parts.append(sep)
            prompt_parts.append(text)
            prompt_parts.append(blank)

        if supplemental_texts:
            prompt_parts.append("## Supplemental Context (Neighbor Pages / Full Short PDFs)")
            for header, sep, text, blank in supplemental_texts:
                prompt_parts.append(header)
                prompt_parts.append(sep)
                prompt_parts.append(text)
                prompt_parts.append(blank)

        prompt_parts.append("## Answer")
        prompt_parts.append("")

        prompt_text = "\n".join(prompt_parts)
        used_docs = top_5 + supplemental_docs

        # Log
        # print(f"[PROMPT] chars={len(prompt_text)} top_docs={len(top_5)} supplemental_pages={len(supplemental_docs)}")
        # print(f"[PROMPT] Preview: {prompt_text[:2000]}...")

        return prompt_text, used_docs, index_map

    def ask_llm(self, prompt: str) -> str:
        """
        Call the LLM with the given prompt and return raw text response.
        """
        # Ensure LLM is initialized
        if not hasattr(self, '_llm') or self._llm is None:
            from .retriever import _build_ollama_llm
            self._llm = _build_ollama_llm(self.cfg)

        # Direct call to LLM
        try:
            response = self._llm(prompt)
            return response
        except Exception as e:
            # print(f"[LLM] Error calling LLM: {e}")
            raise
