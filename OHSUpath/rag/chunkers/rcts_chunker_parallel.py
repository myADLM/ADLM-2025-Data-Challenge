# rag/chunkers/rcts_chunker_parallel.py

from __future__ import annotations

import os
import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain.schema import Document
except Exception:
    from langchain_core.documents import Document

from ..types import Chunk, Chunker
from ..hashing import sha256_str


@dataclass
class SplitCfg:
    chunk_size: int
    chunk_overlap: int
    num_proc: int | str


def _get_src_page(d: Document) -> tuple[str | None, Any]:
    """Best-effort extraction of source path and page number from metadata."""
    md = d.metadata or {}
    src = md.get("source") or md.get("file_path") or md.get("path")
    page = md.get("page", md.get("page_number", md.get("page_no")))
    return src, page


def _sanitize_metadata(md: Dict[str, Any] | None) -> Dict[str, Any]:
    """Make metadata pickle-safe for multiprocessing by stringifying odd types."""
    out: Dict[str, Any] = {}
    for k, v in (md or {}).items():
        try:
            hash(v)  # fast check for simple hashable types
            out[k] = v
        except Exception:
            out[k] = str(v)
    return out


def _make_id(src: str | None, page: Any, content: str, cs: int, co: int) -> str:
    """
    Stable chunk id:
    - includes source, page, chunking params and content
    - first 32 hex chars of sha256 to balance size and collision risk
    """
    s = "" if src is None else str(src)
    p = "" if page is None else str(page)
    base = f"{s}|{p}|{cs}|{co}|{content}"
    return f"{s}::p{p}::{sha256_str(base)[:32]}"


def _split_worker(docs: List[Document], cs: int, co: int) -> List[Chunk]:
    """Split a shard of documents in a single process."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=cs, chunk_overlap=co)
    out: List[Chunk] = []
    for d in splitter.split_documents(docs):
        src, page = _get_src_page(d)
        cid = _make_id(src, page, d.page_content, cs, co)
        md = _sanitize_metadata(d.metadata)
        md.setdefault("chunk_id", cid)  # convenient for downstream tracing
        out.append(
            Chunk(
                chunk_id=cid,
                file_path=src,
                page_no=page,
                content=d.page_content,
                meta=md,
            )
        )
    return out


class RctsChunkerParallel(Chunker):
    """RecursiveCharacterTextSplitter-based chunker with optional multiprocessing."""

    def __init__(self, cfg: SplitCfg):
        self.cfg = cfg

    def _resolve_nproc(self, n_docs: int) -> int:
        """Resolve desired process count with safe bounds."""
        if self.cfg.num_proc == "max":
            cpu = os.cpu_count() or 1
            nproc = cpu
        else:
            try:
                nproc = int(self.cfg.num_proc or 1)
            except Exception:
                nproc = 1
        # Do not spawn more processes than documents
        nproc = max(1, min(nproc, n_docs if n_docs > 0 else 1))
        return nproc

    def split(self, docs: List[Document]) -> List[Chunk]:
        """Split documents into chunks; parallelize when it makes sense."""
        if not docs:
            return []

        nproc = self._resolve_nproc(len(docs))
        cs, co = self.cfg.chunk_size, self.cfg.chunk_overlap

        if nproc <= 1:
            return _split_worker(docs, cs, co)

        size = (len(docs) + nproc - 1) // nproc
        shards = [docs[i : i + size] for i in range(0, len(docs), size)]

        try:
            with mp.Pool(processes=nproc) as pool:
                parts = pool.starmap(_split_worker, [(sh, cs, co) for sh in shards])
        except Exception:
            # Fallback to single-process for environments where mp is flaky
            return _split_worker(docs, cs, co)

        out: List[Chunk] = []
        for p in parts:
            out.extend(p)
        return out
