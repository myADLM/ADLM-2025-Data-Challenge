# rag/retriever.py

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple
import re

from config import load_config
from langchain.chains import RetrievalQA

# Ollama LLM compatibility
_OLLAMA_CLS = None
try:
    from langchain_ollama import OllamaLLM as _OLLAMA_CLS
except Exception:
    try:
        from langchain_community.llms import Ollama as _OLLAMA_CLS
    except Exception:
        _OLLAMA_CLS = None

# ---- LangChain base types ----
try:
    from langchain_core.documents import Document
except Exception:
    from langchain.schema import Document  # fallback

from langchain_core.retrievers import BaseRetriever


# ------------------------
# helpers
# ------------------------

def _cfg_get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _build_ollama_llm(cfg: Any):
    if _OLLAMA_CLS is None:
        raise ImportError(
            "Ollama LLM integration not found. Install `langchain-ollama` or ensure "
            "`langchain_community.llms.Ollama` is available."
        )
    llm_cfg = _cfg_get(cfg, "llm", None)
    model = _cfg_get(llm_cfg, "model", "")
    base_url = _cfg_get(llm_cfg, "base_url", "http://localhost:11434")

    params = dict(_cfg_get(llm_cfg, "params", {}) or {})
    timeout = _cfg_get(llm_cfg, "request_timeout_s", None)
    if timeout is not None:
        params.setdefault("timeout", float(timeout))
    max_retries = _cfg_get(llm_cfg, "max_retries", None)
    if max_retries is not None:
        params.setdefault("max_retries", int(max_retries))
    headers = _cfg_get(llm_cfg, "headers", None)
    if headers:
        params.setdefault("headers", dict(headers))

    return _OLLAMA_CLS(model=model, base_url=base_url, **params)


# ------------------------
# Query type detection
# ------------------------

_KEYWORD_HINTS = re.compile(
    r"(\b\d+(\.\d+)?\s?(?:°?C|°?F|mM|uM|µM|nM|mg/ml|g/l|rpm|pH|\%|v/v|w/v)\b|"
    r"[A-Za-z]*\d+[A-Za-z]*|[_\-/]|cat(?:alog)?[_\-\s]?(?:id|no)\b)",
    re.IGNORECASE
)

class QueryTypeDetector:
    """
    Decide keyword-like vs semantic query behavior based on text, and return:
    - (sparse_w, dense_w)
    - (sparse_k, dense_k)
    """

    def __init__(
        self,
        *,
        weights_keyword: Tuple[float, float] = (0.8, 0.2),
        weights_semantic: Tuple[float, float] = (0.3, 0.7),
        base_sparse_k: int = 80,
        base_dense_k: int = 40,
    ):
        self.w_kw = weights_keyword
        self.w_sem = weights_semantic
        self.ks = int(base_sparse_k)
        self.kd = int(base_dense_k)

    def _is_keywordy(self, q: str) -> bool:
        if not q:
            return False
        toks = [t for t in re.split(r"\s+", q.strip()) if t]
        if _KEYWORD_HINTS.search(q):
            return True
        if len(toks) <= 6:
            return True
        return False

    def decide(self, q: str) -> Tuple[Tuple[float, float], Tuple[int, int]]:
        if self._is_keywordy(q):
            return self.w_kw, (self.ks, self.kd)
        else:
            return self.w_sem, (self.ks, self.kd)


# ------------------------
# Hybrid retriever: subclass BaseRetriever (Pydantic v1 model)
# ------------------------

class HybridBM25FaissRetriever(BaseRetriever):
    """
    LangChain BaseRetriever subclass. Fields are annotated and validated
    by Pydantic (v1-style config).
    """

    # These fields may be callables or custom objects (relaxed validation)
    sparse_search: Any
    dense_search: Any
    id2doc: Any
    id2text: Any

    detector: Any  # QueryTypeDetector
    reranker: Optional[Any] = None
    rerank_mode: str = "auto"     # auto | on | off
    auto_gap_threshold: float = 0.05
    auto_top1_threshold: float = 0.40
    auto_max_rerank: int = 120
    final_k: int = 12

    # Optional: per-source cap and a minimum score threshold
    max_per_source: Optional[int] = None
    min_score: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = False

    # ---------- de-dup helpers ----------
    def _unique_ids_ordered(self, ids: List[str]) -> List[str]:
        """Deduplicate a chunk_id list while preserving order."""
        seen = set()
        out: List[str] = []
        for cid in ids:
            if not cid or cid in seen:
                continue
            seen.add(cid)
            out.append(cid)
        return out

    def _dedup_docs_by_chunk_id(self, docs: List[Document]) -> List[Document]:
        """If upstream passes duplicate Documents, dedupe by metadata['chunk_id']."""
        seen = set()
        out: List[Document] = []
        for d in docs:
            md = getattr(d, "metadata", {}) or {}
            cid = md.get("chunk_id")
            if cid:
                key = cid
            else:
                # Extreme fallback: use (source, content prefix)
                key = (md.get("source"), d.page_content[:64])
            if key in seen:
                continue
            seen.add(key)
            out.append(d)
        return out

    # LangChain requires this (run_manager kept for newer interfaces)
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        (w_s, w_d), (ks, kd) = self.detector.decide(query)

        # 1) sparse candidates
        sparse_hits = self.sparse_search(query, ks) if ks > 0 else []

        # n-gram auto/forced re-ranking (robustness)
        if self.reranker and (self.rerank_mode in {"on", "auto"}):
            do_rerank = (self.rerank_mode == "on")
            if self.rerank_mode == "auto" and sparse_hits:
                scores = [s for _, s in sparse_hits]
                mx = max(scores) if scores else 0.0
                top1 = scores[0] if scores else 0.0
                gap = (scores[0] - scores[1]) / (mx + 1e-12) if len(scores) >= 2 else 1.0
                if top1 < self.auto_top1_threshold or gap < self.auto_gap_threshold:
                    do_rerank = True
            if do_rerank:
                # Pass (id, score); reranker uses id2text to fetch text
                candidates = [(cid, sc) for cid, sc in sparse_hits[: self.auto_max_rerank]]

                # Try new signature; fallback to old if needed
                try:
                    new_sparse = self.reranker.rerank(query, candidates, self.id2text)
                except TypeError:
                    new_sparse = self.reranker.rerank(query, candidates)

                # Normalize to List[(id, score)]
                def _norm_pairs(items):
                    out = []
                    if not items:
                        return out
                    for it in items:
                        if isinstance(it, (list, tuple)):
                            if len(it) >= 2:
                                cid, sc = it[0], it[1]
                            elif len(it) == 1:
                                cid, sc = it[0], 0.0
                            else:
                                continue
                        else:
                            cid, sc = it, 0.0
                        if cid is None:
                            continue
                        try:
                            sc = float(sc)
                        except Exception:
                            sc = 0.0
                        out.append((cid, sc))
                    return out

                new_sparse = _norm_pairs(new_sparse)
                if not new_sparse:
                    new_sparse = candidates  # fallback

                sparse_hits = new_sparse + sparse_hits[self.auto_max_rerank:]

        # 2) dense candidates
        dense_hits = self.dense_search(query, kd) if kd > 0 else []

        # 3) normalize and fuse (use cid as key to dedupe)
        def _to_norm_dict(hits: List[Tuple[str, float]]) -> Dict[str, float]:
            if not hits:
                return {}
            vals = [s for _, s in hits]
            mn, mx = min(vals), max(vals)
            den = (mx - mn) if (mx - mn) > 1e-12 else 1.0
            return {cid: (s - mn) / den for cid, s in hits}

        s_norm = _to_norm_dict(sparse_hits)
        d_norm = _to_norm_dict(dense_hits)

        combined: Dict[str, float] = {}
        keys = set(s_norm) | set(d_norm)
        for cid in keys:
            combined[cid] = w_s * s_norm.get(cid, 0.0) + w_d * d_norm.get(cid, 0.0)

        # rank
        top = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        # score threshold
        if self.min_score is not None:
            top = [(cid, s) for cid, s in top if s >= float(self.min_score)]

        # unique ids, per-source cap, then truncate to final_k
        top_ids = [cid for cid, _ in top]
        top_ids = self._unique_ids_ordered(top_ids)

        if self.max_per_source and self.max_per_source > 0:
            kept: List[str] = []
            per_src: Dict[str, int] = {}
            for cid in top_ids:
                try:
                    doc = self.id2doc(cid)
                except KeyError:
                    continue
                md = getattr(doc, "metadata", {}) or {}
                src = md.get("source") or md.get("file_path") or md.get("path") or "?"
                cnt = per_src.get(src, 0)
                if cnt < int(self.max_per_source):
                    kept.append(cid)
                    per_src[src] = cnt + 1
            top_ids = kept

        top_ids = top_ids[: self.final_k]

        # fetch documents
        docs: List[Document] = []
        for cid in top_ids:
            try:
                docs.append(self.id2doc(cid))
            except KeyError:
                continue

        # final dedupe by chunk_id as a safety net
        docs = self._dedup_docs_by_chunk_id(docs)

        return docs

    # Optional: async version (LangChain will prefer sync)
    async def _aget_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        return self._get_relevant_documents(query, run_manager=run_manager)


# ------------------------
# QA chain builder
# ------------------------

def build_qa(
    retriever,
    cfg: Any = None,
    *,
    yaml_path: str = "config.yaml",
    use_yaml: bool = True,
) -> RetrievalQA | dict:
    """
    Build a RetrievalQA chain using config. If cfg is None, load config.
    """
    if cfg is None:
        cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)

    llm_cfg = _cfg_get(cfg, "llm", None)

    if not _cfg_get(llm_cfg, "enabled", True):
        return {"ok": True, "llm": "disabled"}

    provider = str(_cfg_get(llm_cfg, "provider", "ollama")).lower()
    if provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {_cfg_get(llm_cfg, 'provider', '')}")

    llm = _build_ollama_llm(cfg)

    chain_type_kwargs = _cfg_get(llm_cfg, "chain_type_kwargs", None)

    kwargs = dict(
        llm=llm,
        chain_type=str(_cfg_get(llm_cfg, "chain_type", "stuff")),
        retriever=retriever,
        return_source_documents=True,
    )
    if chain_type_kwargs:
        kwargs["chain_type_kwargs"] = chain_type_kwargs

    return RetrievalQA.from_chain_type(**kwargs)
