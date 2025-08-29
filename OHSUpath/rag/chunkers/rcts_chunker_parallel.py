# rag/chunkers/rcts_chunker_parallel.py

from __future__ import annotations

import os
import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Any, Sequence
from config import load_config

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
    source_keys: Sequence[str] = ("source", "file_path", "path")
    page_keys: Sequence[str] = ("page", "page_number", "page_no")
    chunk_id_hash_len: int = 32


def _get_src_page(d: Document, source_keys: Sequence[str], page_keys: Sequence[str]) -> tuple[str | None, Any]:
    """Extract source path and page number using configured key priorities."""
    md = d.metadata or {}
    src = next((md[k] for k in source_keys if k in md and md[k] is not None), None)
    page = next((md[k] for k in page_keys if k in md and md[k] is not None), None)
    return src, page


def _sanitize_metadata(md: Dict[str, Any] | None) -> Dict[str, Any]:
    """Make metadata pickle-safe for multiprocessing."""
    out: Dict[str, Any] = {}
    for k, v in (md or {}).items():
        try:
            hash(v)
            out[k] = v
        except Exception:
            out[k] = str(v)
    return out


def _make_id(src: str | None, page: Any, content: str, cs: int, co: int, hash_len: int) -> str:
    """Generate stable chunk_id with configurable hash length."""
    s = "" if src is None else str(src)
    p = "" if page is None else str(page)
    base = f"{s}|{p}|{cs}|{co}|{content}"
    n = max(8, min(int(hash_len or 32), 64))
    return f"{s}::p{p}::{sha256_str(base)[:n]}"


def _split_worker(
    docs: List[Document],
    cs: int,
    co: int,
    source_keys: Sequence[str],
    page_keys: Sequence[str],
    hash_len: int,
) -> List[Chunk]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=cs, chunk_overlap=co)
    out: List[Chunk] = []
    for d in splitter.split_documents(docs):
        src, page = _get_src_page(d, source_keys, page_keys)
        cid = _make_id(src, page, d.page_content, cs, co, hash_len)
        md = _sanitize_metadata(d.metadata)
        md.setdefault("chunk_id", cid)
        out.append(Chunk(chunk_id=cid, file_path=src, page_no=page, content=d.page_content, meta=md))
    return out


class RctsChunkerParallel(Chunker):
    """RecursiveCharacterTextSplitter-based chunker with optional multiprocessing."""

    def __init__(self, cfg: SplitCfg | None = None):
        if cfg is None:
            if not load_config:
                raise RuntimeError("Config loader not available; pass cfg manually.")
            app_cfg = load_config()
            cfg = SplitCfg(
                chunk_size=app_cfg.split.chunk_size,
                chunk_overlap=app_cfg.split.chunk_overlap,
                num_proc=getattr(app_cfg.split, "num_proc", "max"),
                source_keys=getattr(app_cfg.split, "source_keys", ["source", "file_path", "path"]),
                page_keys=getattr(app_cfg.split, "page_keys", ["page", "page_number", "page_no"]),
                chunk_id_hash_len=getattr(app_cfg.hashing, "chunk_id_hash_len", 32),
            )
        self.cfg = cfg

    def _resolve_nproc(self, n_docs: int) -> int:
        if self.cfg.num_proc == "max":
            nproc = os.cpu_count() or 1
        else:
            try:
                nproc = int(self.cfg.num_proc or 1)
            except Exception:
                nproc = 1
        return max(1, min(nproc, n_docs if n_docs > 0 else 1))

    def split(self, docs: List[Document]) -> List[Chunk]:
        if not docs:
            return []
        nproc = self._resolve_nproc(len(docs))
        cs, co = self.cfg.chunk_size, self.cfg.chunk_overlap
        src_keys, pg_keys, hlen = self.cfg.source_keys, self.cfg.page_keys, self.cfg.chunk_id_hash_len

        if nproc <= 1:
            return _split_worker(docs, cs, co, src_keys, pg_keys, hlen)

        size = (len(docs) + nproc - 1) // nproc
        shards = [docs[i : i + size] for i in range(0, len(docs), size)]
        try:
            with mp.Pool(processes=nproc) as pool:
                parts = pool.starmap(
                    _split_worker,
                    [(sh, cs, co, src_keys, pg_keys, hlen) for sh in shards],
                )
        except Exception:
            return _split_worker(docs, cs, co, src_keys, pg_keys, hlen)

        out: List[Chunk] = []
        for p in parts:
            out.extend(p)
        return out
