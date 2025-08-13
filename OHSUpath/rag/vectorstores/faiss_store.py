# rag/vectorstores/faiss_store.py

from __future__ import annotations
import os, json, tempfile, hashlib
from typing import List, Dict, Any, Callable, Optional, Union

import numpy as np, faiss
from langchain_community.vectorstores import FAISS as LCFAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

try:
    from langchain_core.documents import Document
except Exception:
    from langchain.schema import Document

try:
    from langchain_core.embeddings import Embeddings
except Exception:
    from langchain.embeddings.base import Embeddings

from ..types import VectorIndex, Chunk

# small epsilon to avoid division-by-zero in normalization
EPS = 1e-12


def _model_sig(model_name: str) -> str:
    return hashlib.sha256(model_name.encode("utf-8")).hexdigest()[:16]


def _atomic_write(path: str, text: str, encoding: str = "utf-8") -> None:
    """Atomic text write: write to temp, fsync, replace."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


class _CallableToEmbeddingsAdapter(Embeddings):
    """Wrap a callable as an Embeddings object.
    If normalize=True (used in IP mode), outputs unit vectors (cosine-like).
    """
    def __init__(self, fn, normalize: bool = False):
        self._fn = fn
        self._normalize = normalize

    def _maybe_norm(self, v):
        if not self._normalize:
            return v
        arr = np.asarray(v, dtype=np.float32)
        if arr.ndim == 1:
            n = np.linalg.norm(arr) + EPS
            return (arr / n).tolist()
        else:
            n = np.linalg.norm(arr, axis=1, keepdims=True) + EPS
            return (arr / n).astype(np.float32).tolist()

    def embed_query(self, text: str):
        try:
            out = self._fn(text)
        except TypeError:
            out = self._fn([text])[0]
        if isinstance(out, np.ndarray):
            out = out.astype(np.float32).tolist()
        return self._maybe_norm(out)

    def embed_documents(self, texts):
        out = self._fn(texts)
        if isinstance(out, np.ndarray):
            out = out.astype(np.float32).tolist()
        return self._maybe_norm(out)


class FaissIndex(VectorIndex):
    """FAISS index with save/load and retriever support."""
    def __init__(
        self,
        embedding_dim: int,
        model_name: str,
        metric: str = "l2",
        *,
        strict_meta_check: bool = True,   # raise on meta mismatch
        clear_on_delete: bool = True,     # delete_by_chunk_ids clears all
        file_encoding: str = "utf-8",     # JSON read/write encoding
    ):
        if metric not in {"l2", "ip"}:
            raise ValueError("metric must be 'l2' or 'ip'")
        self._dim = int(embedding_dim)
        self._metric = metric
        self._model_name = model_name
        self._index = faiss.IndexFlatL2(self._dim) if metric == "l2" else faiss.IndexFlatIP(self._dim)
        self._docstore = InMemoryDocstore({})
        self._id_map: Dict[int, str] = {}
        self._meta: Dict[str, Any] = {
            "embedding_dim": self._dim,
            "metric": self._metric,
            "model_sig": _model_sig(self._model_name),
            "schema_version": 1,
        }
        self._strict_meta_check = bool(strict_meta_check)
        self._clear_on_delete = bool(clear_on_delete)
        self._file_encoding = file_encoding

    # ---------- paths ----------
    def _paths(self, dirpath: str) -> Dict[str, str]:
        return dict(
            index=os.path.join(dirpath, "index.faiss"),
            idmap=os.path.join(dirpath, "id_map.json"),
            doc=os.path.join(dirpath, "docstore.json"),
            meta=os.path.join(dirpath, "index.meta.json"),
        )

    # ---------- load/save ----------
    def load_or_init(self, dirpath: str) -> None:
        os.makedirs(dirpath, exist_ok=True)
        p = self._paths(dirpath)
        if all(os.path.exists(x) for x in p.values()):
            self._index = faiss.read_index(p["index"])

            with open(p["idmap"], "r", encoding=self._file_encoding) as f:
                raw_idmap = json.load(f)

            if isinstance(raw_idmap, list):
                # support both legacy formats:
                # 1) [[row, "chunk_id"], ...]
                # 2) ["chunk_id0", "chunk_id1", ...]
                if raw_idmap and isinstance(raw_idmap[0], (list, tuple)) and len(raw_idmap[0]) == 2:
                    self._id_map = {int(k): v for k, v in raw_idmap}
                else:
                    self._id_map = {i: v for i, v in enumerate(raw_idmap)}
            else:
                self._id_map = {int(k): v for k, v in raw_idmap.items()}


            with open(p["doc"], "r", encoding=self._file_encoding) as f:
                raw_docs = json.load(f)
            self._docstore._dict = {
                k: Document(page_content=v["page_content"], metadata=v["metadata"])
                for k, v in raw_docs.items()
            }

            with open(p["meta"], "r", encoding=self._file_encoding) as f:
                meta = json.load(f)
            ok = (
                int(meta.get("embedding_dim")) == self._dim
                and meta.get("metric") == self._metric
                and meta.get("model_sig") == _model_sig(self._model_name)
            )
            if not ok:
                if self._strict_meta_check:
                    raise RuntimeError("Index meta mismatch: please rebuild index.")
                # soft reset when meta mismatch and strict check is off
                self._index = faiss.IndexFlatL2(self._dim) if self._metric == "l2" else faiss.IndexFlatIP(self._dim)
                self._id_map.clear()
                self._docstore._dict.clear()
                self._meta = {
                    "embedding_dim": self._dim,
                    "metric": self._metric,
                    "model_sig": _model_sig(self._model_name),
                    "schema_version": 1,
                }
                return
            self._meta = meta

    def persist_atomic(self, dirpath: str) -> None:
        os.makedirs(dirpath, exist_ok=True)
        p = self._paths(dirpath)

        # atomic write for faiss index
        fd, tmp = tempfile.mkstemp(dir=dirpath)
        try:
            os.close(fd)
            faiss.write_index(self._index, tmp)
            os.replace(tmp, p["index"])
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

        # atomic write for id_map/doc/meta
        idmap_payload = {str(k): v for k, v in self._id_map.items()}
        _atomic_write(p["idmap"], json.dumps(idmap_payload, ensure_ascii=False), self._file_encoding)

        raw = {
            k: {"page_content": v.page_content, "metadata": v.metadata}
            for k, v in self._docstore._dict.items()
        }
        _atomic_write(p["doc"], json.dumps(raw, ensure_ascii=False), self._file_encoding)

        _atomic_write(p["meta"], json.dumps(self._meta, ensure_ascii=False, indent=2), self._file_encoding)

    # ---------- in-memory ops ----------
    def _ensure_float32_2d(self, arr: np.ndarray) -> np.ndarray:
        """Ensure shape (n, d) and dtype float32."""
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.ndim != 2:
            raise ValueError(f"expected (n, d) array, got shape={arr.shape}")
        if arr.dtype != np.float32:
            arr = arr.astype(np.float32, copy=False)
        return arr

    def upsert(self, chunks: List[Chunk], vectors: List[List[float]]) -> None:
        """Add vectors and map FAISS row -> chunk_id."""
        if not chunks:
            return
        if len(chunks) != len(vectors):
            raise ValueError(f"chunks ({len(chunks)}) and vectors ({len(vectors)}) mismatch")

        arr = self._ensure_float32_2d(np.asarray(vectors, dtype=np.float32))
        if arr.shape[1] != self._dim:
            raise ValueError(f"embedding_dim mismatch: expected {self._dim}, got {arr.shape[1]}")

        # cosine flow: normalize store vectors in IP mode
        if self._metric == "ip":
            norms = np.linalg.norm(arr, axis=1, keepdims=True) + EPS
            arr = arr / norms

        start = int(self._index.ntotal)
        self._index.add(arr)

        for i, c in enumerate(chunks):
            self._docstore._dict[c.chunk_id] = Document(page_content=c.content, metadata=c.meta)
            self._id_map[start + i] = c.chunk_id

    def delete_by_chunk_ids(self, ids: List[str]) -> None:
        """Safety-first: rebuild index if any id is passed (optional no-op)."""
        if not ids:
            return
        if not self._clear_on_delete:
            return  # no-op (upper layer may rebuild selectively)
        self._index = faiss.IndexFlatL2(self._dim) if self._metric == "l2" else faiss.IndexFlatIP(self._dim)
        self._id_map.clear()
        self._docstore._dict.clear()

    # ---------- retriever ----------
    def as_retriever(
        self,
        k: int,
        search_type: str = "similarity",
        embedding: Optional[Union[object, Callable[..., Any]]] = None,
        *,
        normalize_query_in_ip: Optional[bool] = None,      # if None, follow metric
        search_kwargs: Optional[Dict[str, Any]] = None,     # e.g. {"k": k, "fetch_k": 50}
    ):
        """Build a LangChain retriever on this index.
        - embedding: Embeddings or callable(text|list[str]) -> vector(s)
        - normalize_query_in_ip: if None, follows metric; else force on/off
        - search_kwargs: extra kwargs for LC retriever (fetch_k, etc.)
        """
        if embedding is None:
            raise ValueError("embedding is required (Embeddings instance or callable).")

        # decide query normalization policy (cosine flow in IP mode)
        norm_flag = (self._metric == "ip") if normalize_query_in_ip is None else bool(normalize_query_in_ip)

        if callable(embedding):
            embedding_obj = _CallableToEmbeddingsAdapter(embedding, normalize=norm_flag)
        else:
            if not hasattr(embedding, "embed_query"):
                raise TypeError("embedding must implement .embed_query(text) -> List[float]")
            embedding_obj = embedding

        vs = LCFAISS(
            index=self._index,
            embedding_function=embedding_obj,
            docstore=self._docstore,
            index_to_docstore_id=self._id_map,
        )
        kwargs = {"k": k}
        if search_kwargs:
            kwargs.update(search_kwargs)
        return vs.as_retriever(search_type=search_type, search_kwargs=kwargs)
