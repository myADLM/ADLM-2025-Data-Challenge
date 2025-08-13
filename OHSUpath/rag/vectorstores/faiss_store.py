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


def _model_sig(model_name: str) -> str:
    return hashlib.sha256(model_name.encode("utf-8")).hexdigest()[:16]


def _atomic_write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
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
    def __init__(self, fn, normalize: bool = False):
        self._fn = fn
        self._normalize = normalize

    def _maybe_norm(self, v):
        if not self._normalize:
            return v
        arr = np.asarray(v, dtype=np.float32)
        if arr.ndim == 1:
            n = np.linalg.norm(arr) + 1e-12
            return (arr / n).tolist()
        else:
            n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
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
    def __init__(self, embedding_dim: int, model_name: str, metric: str = "l2"):
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


    def _paths(self, dirpath: str) -> Dict[str, str]:
        return dict(
            index=os.path.join(dirpath, "index.faiss"),
            idmap=os.path.join(dirpath, "id_map.json"),
            doc=os.path.join(dirpath, "docstore.json"),
            meta=os.path.join(dirpath, "index.meta.json"),
        )

    def load_or_init(self, dirpath: str) -> None:
        os.makedirs(dirpath, exist_ok=True)
        p = self._paths(dirpath)
        if all(os.path.exists(x) for x in p.values()):
            self._index = faiss.read_index(p["index"])

            with open(p["idmap"], "r", encoding="utf-8") as f:
                raw_idmap = json.load(f)
            if isinstance(raw_idmap, list):
                self._id_map = {int(k): v for k, v in raw_idmap}
            else:
                self._id_map = {int(k): v for k, v in raw_idmap.items()}

            with open(p["doc"], "r", encoding="utf-8") as f:
                raw_docs = json.load(f)
            self._docstore._dict = {
                k: Document(page_content=v["page_content"], metadata=v["metadata"])
                for k, v in raw_docs.items()
            }

            with open(p["meta"], "r", encoding="utf-8") as f:
                meta = json.load(f)
            ok = (
                int(meta.get("embedding_dim")) == self._dim
                and meta.get("metric") == self._metric
                and meta.get("model_sig") == _model_sig(self._model_name)
            )
            if not ok:
                raise RuntimeError("Index meta mismatch: please rebuild index.")
            self._meta = meta

    def persist_atomic(self, dirpath: str) -> None:
        os.makedirs(dirpath, exist_ok=True)
        p = self._paths(dirpath)

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

        idmap_payload = {str(k): v for k, v in self._id_map.items()}
        _atomic_write(p["idmap"], json.dumps(idmap_payload, ensure_ascii=False))

        raw = {
            k: {"page_content": v.page_content, "metadata": v.metadata}
            for k, v in self._docstore._dict.items()
        }
        _atomic_write(p["doc"], json.dumps(raw, ensure_ascii=False))

        _atomic_write(p["meta"], json.dumps(self._meta, ensure_ascii=False, indent=2))


    def _ensure_float32_2d(self, arr: np.ndarray) -> np.ndarray:
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.ndim != 2:
            raise ValueError(f"expected (n, d) array, got shape={arr.shape}")
        if arr.dtype != np.float32:
            arr = arr.astype(np.float32, copy=False)
        return arr

    def upsert(self, chunks: List[Chunk], vectors: List[List[float]]) -> None:
        if not chunks:
            return
        if len(chunks) != len(vectors):
            raise ValueError(f"chunks ({len(chunks)}) and vectors ({len(vectors)}) mismatch")

        arr = self._ensure_float32_2d(np.asarray(vectors, dtype=np.float32))
        if arr.shape[1] != self._dim:
            raise ValueError(f"embedding_dim mismatch: expected {self._dim}, got {arr.shape[1]}")

        if self._metric == "ip":
            norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
            arr = arr / norms

        start = int(self._index.ntotal)
        self._index.add(arr)

        for i, c in enumerate(chunks):
            self._docstore._dict[c.chunk_id] = Document(page_content=c.content, metadata=c.meta)
            self._id_map[start + i] = c.chunk_id

    def delete_by_chunk_ids(self, ids: List[str]) -> None:
        if not ids:
            return
        self._index = faiss.IndexFlatL2(self._dim) if self._metric == "l2" else faiss.IndexFlatIP(self._dim)
        self._id_map.clear()
        self._docstore._dict.clear()


    def as_retriever(
        self,
        k: int,
        search_type: str = "similarity",
        embedding: Optional[Union[object, Callable[..., Any]]] = None,
    ):
        if embedding is None:
            raise ValueError("embedding is required (Embeddings instance or callable).")
        if callable(embedding):
            embedding_obj = _CallableToEmbeddingsAdapter(embedding, normalize=(self._metric == "ip"))
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
        return vs.as_retriever(search_type=search_type, search_kwargs={"k": k})
