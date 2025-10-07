# rag/vectorstores/bm25_store.py

from __future__ import annotations
import os
import json
import math
from typing import List, Tuple, Optional, Any

# ---- optional deps (silent) ----
_HAS_BM25S = False
try:
    import bm25s  # type: ignore
    _HAS_BM25S = True
except Exception:
    _HAS_BM25S = False

_HAS_RANK = False
try:
    from rank_bm25 import BM25Okapi  # type: ignore
    _HAS_RANK = True
except Exception:
    _HAS_RANK = False

# ---- small utils ----
def _simple_tokenize(s: str) -> List[str]:
    """
    Lightweight tokenizer:
      - lowercases
      - splits on non-alphanumerics
      - treats '_' and '-' as spaces for better robustness (e.g., 'aa_inf3', 'aa-inf3')
    Used for rank_bm25; bm25s uses its own tokenizer.
    """
    import re
    s = s.lower()
    s = s.replace("_", " ").replace("-", " ")
    return re.findall(r"[a-z0-9]+", s)

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def _is_dir_with(path: str, required_files: List[str]) -> bool:
    if not os.path.isdir(path):
        return False
    for f in required_files:
        if not os.path.exists(os.path.join(path, f)):
            return False
    return True


class BM25SparseIndex:
    """
    A tiny unifying wrapper for bm25s (default) with silent fallback to rank_bm25.

    API:
      - build(items: List[Tuple[str, str]])
      - search(query: str, k: int) -> List[Tuple[str, float]]  # [(chunk_id, score)]
      - save(path: str)   # path is treated as a DIRECTORY for both backends
      - load(path: str) -> BM25SparseIndex
    """
    def __init__(
        self,
        backend: str = "bm25s",
        *,
        stopwords: Optional[str | List[str]] = "en",
        stemmer: Optional[Any] = None,
    ):
        # backend is a preference. We silently fallback if needed.
        self.backend = backend.lower() if backend else "bm25s"
        self._effective_backend = None  # "bm25s" | "rank_bm25"
        self._bm25 = None
        self._id_list: List[str] = []
        self._stopwords = stopwords
        self._stemmer = stemmer
        # for rank_bm25 rebuild when loading
        self._tokenized_corpus: Optional[List[List[str]]] = None

    # ---------- build ----------
    def build(self, items: List[Tuple[str, str]]) -> None:
        """
        items: [(chunk_id, text), ...]
        """
        self._id_list = [cid for cid, _ in items]
        corpus = [txt if isinstance(txt, str) else str(txt) for _, txt in items]

        if self.backend == "bm25s" and _HAS_BM25S:
            # bm25s path (preferred)
            corpus_tokens = bm25s.tokenize(corpus, stopwords=self._stopwords, stemmer=self._stemmer)
            retriever = bm25s.BM25()
            retriever.index(corpus_tokens)
            self._bm25 = retriever
            self._effective_backend = "bm25s"
            self._tokenized_corpus = None  # not needed
            return

        # fallback to rank_bm25 (silent)
        if not _HAS_RANK and _HAS_BM25S:
            # still try bm25s if rank_bm25 is not available
            corpus_tokens = bm25s.tokenize(corpus, stopwords=self._stopwords, stemmer=self._stemmer)
            retriever = bm25s.BM25()
            retriever.index(corpus_tokens)
            self._bm25 = retriever
            self._effective_backend = "bm25s"
            self._tokenized_corpus = None
            return

        if not _HAS_RANK and not _HAS_BM25S:
            raise RuntimeError(
                "Neither bm25s nor rank_bm25 is available. Please install one of them."
            )

        # rank_bm25 path
        tokenized = [_simple_tokenize(t) for t in corpus]
        self._bm25 = BM25Okapi(tokenized)
        self._effective_backend = "rank_bm25"
        self._tokenized_corpus = tokenized

    # ---------- search ----------
    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        if self._bm25 is None or not self._id_list:
            return []

        k = max(1, int(k))
        if self._effective_backend == "bm25s":
            # bm25s: tokenize -> retrieve
            qtok = bm25s.tokenize(query, stopwords=self._stopwords, stemmer=self._stemmer)
            # Single-query compatibility: if 1D list[int], wrap to [list[int]]
            if isinstance(qtok, list) and (len(qtok) == 0 or isinstance(qtok[0], int)):
                qtok = [qtok]
            results, scores = self._bm25.retrieve(qtok, k=k)
            # take the first query result
            idxs = results[0].tolist() if hasattr(results, "tolist") else list(results[0])
            scs = scores[0].tolist() if hasattr(scores, "tolist") else list(scores[0])
            out: List[Tuple[str, float]] = []
            for i, s in zip(idxs, scs):
                if i is None or i < 0 or i >= len(self._id_list):
                    continue
                out.append((self._id_list[int(i)], float(s)))
            return out

        # rank_bm25
        toks = _simple_tokenize(query)
        scores = self._bm25.get_scores(toks)  # ndarray-like
        try:
            import numpy as np
            order = np.argsort(-scores)[:k]
            return [(self._id_list[i], float(scores[i])) for i in order]
        except Exception:
            # Rare environments without numpy
            pairs = list(enumerate([float(s) for s in scores]))
            pairs.sort(key=lambda x: -x[1])
            pairs = pairs[:k]
            return [(self._id_list[i], s) for i, s in pairs]

    # ---------- persist ----------
    def save(self, path: str) -> None:
        """
        Save index into a directory `path`.
        - bm25s: use bm25.save(path) + id_map.json
        - rank_bm25: write tokenized_corpus.json + id_map.json
        """
        _ensure_dir(path)
        # write meta for both
        meta = {
            "backend": self._effective_backend or self.backend,
            "stopwords": self._stopwords if isinstance(self._stopwords, str) else "custom",
        }
        with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)

        with open(os.path.join(path, "id_map.json"), "w", encoding="utf-8") as f:
            json.dump(self._id_list, f, ensure_ascii=False)

        if self._effective_backend == "bm25s":
            # bm25s knows how to save into a directory
            self._bm25.save(path)
            return

        # rank_bm25: save tokenized_corpus for later rebuild
        if self._tokenized_corpus is None:
            raise RuntimeError("rank_bm25 requires tokenized corpus to save.")
        with open(os.path.join(path, "tokenized_corpus.json"), "w", encoding="utf-8") as f:
            json.dump(self._tokenized_corpus, f, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "BM25SparseIndex":
        """
        Load from a directory created by `save`.
        """
        if not os.path.isdir(path):
            raise FileNotFoundError(f"BM25SparseIndex path not found: {path}")

        # core files
        meta_path = os.path.join(path, "meta.json")
        idmap_path = os.path.join(path, "id_map.json")
        if not (os.path.exists(meta_path) and os.path.exists(idmap_path)):
            raise RuntimeError(f"Invalid BM25SparseIndex folder (missing meta/id_map): {path}")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        with open(idmap_path, "r", encoding="utf-8") as f:
            id_list = json.load(f)

        backend = (meta.get("backend") or "bm25s").lower()
        stopwords = meta.get("stopwords", "en")

        inst = cls(backend=backend, stopwords=stopwords)
        inst._id_list = id_list

        if backend == "bm25s" and _HAS_BM25S:
            # let bm25s restore from the directory
            inst._bm25 = bm25s.BM25.load(path, load_corpus=False)
            inst._effective_backend = "bm25s"
            inst._tokenized_corpus = None
            return inst

        # rank_bm25 rebuild
        tok_path = os.path.join(path, "tokenized_corpus.json")
        if not os.path.exists(tok_path):
            # if rank mode is missing tokenized_corpus, try to fallback to bm25s (dir may contain bm25s files)
            if _HAS_BM25S:
                inst._bm25 = bm25s.BM25.load(path, load_corpus=False)
                inst._effective_backend = "bm25s"
                inst._tokenized_corpus = None
                return inst
            raise RuntimeError("rank_bm25 index missing tokenized_corpus.json and bm25s not available.")

        if not _HAS_RANK:
            # without rank_bm25, try bm25s load (if present)
            if _HAS_BM25S and _is_dir_with(path, ["bm25_a.npz", "bm25_b.npz"]):
                inst._bm25 = bm25s.BM25.load(path, load_corpus=False)
                inst._effective_backend = "bm25s"
                inst._tokenized_corpus = None
                return inst
            raise RuntimeError("rank_bm25 not available to load saved rank index.")

        with open(tok_path, "r", encoding="utf-8") as f:
            tokenized_corpus = json.load(f)
        inst._bm25 = BM25Okapi(tokenized_corpus)
        inst._effective_backend = "rank_bm25"
        inst._tokenized_corpus = tokenized_corpus
        return inst
