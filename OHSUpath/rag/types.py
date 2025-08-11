# rag/types.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List, Dict, Optional, Tuple, runtime_checkable
from langchain.schema import Document

@dataclass(frozen=True)
class FileMeta:
    path: str
    size: int
    mtime: float
    sha256: str

@dataclass
class Chunk:
    chunk_id: str
    file_path: str
    page_no: Optional[int]
    content: str
    meta: Dict

@dataclass
class DiffResult:
    added: List[FileMeta]
    removed: List[FileMeta]
    modified: List[Tuple[FileMeta, FileMeta]]

@runtime_checkable
class DocumentLoader(Protocol):
    def discover(self, root: str, exts: List[str]) -> List[str]: ...
    def load(self, path: str) -> List[Document]: ...

@runtime_checkable
class Chunker(Protocol):
    def split(self, docs: List[Document]) -> List[Chunk]: ...

@runtime_checkable
class Embedder(Protocol):
    embedding_dim: int
    model_name: str
    def embed(self, texts: List[str]) -> List[List[float]]: ...

@runtime_checkable
class VectorIndex(Protocol):
    def load_or_init(self, dirpath: str) -> None: ...
    def upsert(self, chunks: List[Chunk], vectors: List[List[float]]) -> None: ...
    def delete_by_chunk_ids(self, ids: List[str]) -> None: ...
    def persist_atomic(self, dirpath: str) -> None: ...
    def as_retriever(self, k: int, search_type: str): ...

