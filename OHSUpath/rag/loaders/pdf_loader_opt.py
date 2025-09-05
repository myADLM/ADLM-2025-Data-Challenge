# rag/loaders/pdf_loader_opt.py

from __future__ import annotations
from typing import List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import os, math, multiprocessing as mp
import fitz
from ..types import Document, DocumentLoader
from config import load_config
fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

@dataclass
class LoaderCfg:
    exts: List[str]
    prefetch_budget_mb: int
    io_batch_files: int
    num_proc: int | str
    pdf_text_mode: str = "text"


def _read_bytes_with_budget(paths: List[str], byte_budget: int) -> Tuple[List[Tuple[str, bytes]], int]:
    items: List[Tuple[str, bytes]] = []
    used = 0
    for p in paths:
        try:
            sz = os.path.getsize(p)
            if used and used + sz > byte_budget:
                break
            with open(p, "rb") as f:
                b = f.read()
            items.append((p, b))
            used += len(b)
        except Exception:
            continue
    return items, used

def _decode_pdf_bytes(data: bytes, text_mode: str, path: str) -> List[Document]:
    pages: List[Document] = []
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            for i in range(doc.page_count):
                t = doc.load_page(i).get_text(text_mode).strip()
                if t:
                    pages.append(
                        Document(
                            page_content=t,
                            metadata={
                                "source": path,
                                "page": i,              # 0-based
                                "page_index": i,        # 0-based
                                "page_number": i + 1,   # 1-based
                            },
                        )
                    )
    except Exception as e:
        pages.append(
            Document(
                page_content="",
                metadata={"source": path, "parse_error": True, "error": repr(e)},
            )
        )
    return pages

def _worker(in_q: mp.Queue, out_q: mp.Queue, text_mode: str) -> None:
    while True:
        item = in_q.get()
        if item is None:
            out_q.put(None)
            break
        batch_id, file_items = item
        docs: List[Document] = []
        for path, b in file_items:
            docs.extend(_decode_pdf_bytes(b, text_mode, path))
        out_q.put((batch_id, docs))


class PdfLoaderOptimized(DocumentLoader):
    def __init__(self, cfg: LoaderCfg | None = None, *, yaml_path: str = "config.yaml", use_yaml: bool = True):
        if cfg is None:
            app_cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)
            cfg = LoaderCfg(
                exts=[e.lower() for e in (app_cfg.paths.allowed_extensions or [".pdf"])],
                pdf_text_mode=app_cfg.paths.pdf_text_mode or "text",
                prefetch_budget_mb=max(1, int(app_cfg.pdf_loader.prefetch_budget_mb or 1)),
                io_batch_files=max(1, int(app_cfg.pdf_loader.io_batch_files or 1)),
                num_proc=app_cfg.pdf_loader.num_proc if app_cfg.pdf_loader.num_proc is not None else "max",
            )
        self.cfg = cfg

    @classmethod
    def from_config(cls, yaml_path: str = "config.yaml", use_yaml: bool = True) -> "PdfLoaderOptimized":
        return cls(None, yaml_path=yaml_path, use_yaml=use_yaml)

    def discover(self, root: str, exts: List[str] | None = None) -> List[str]:
        exts = [e.lower() for e in (exts or self.cfg.exts)]
        files: List[str] = []
        for p in Path(root).rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                files.append(str(p))
        files.sort()
        return files

    def load(self, path: str) -> List[Document]:
        out: List[Document] = []
        try:
            with fitz.open(path) as doc:
                for i in range(doc.page_count):
                    t = doc.load_page(i).get_text(self.cfg.pdf_text_mode).strip()
                    if t:
                        out.append(
                            Document(
                                page_content=t,
                                metadata={
                                    "source": path,
                                    "page": i,
                                    "page_index": i,
                                    "page_number": i + 1,
                                },
                            )
                        )
        except Exception as e:
            out.append(
                Document(
                    page_content="",
                    metadata={"source": path, "parse_error": True, "error": repr(e)},
                )
            )
        return out


    def load_many_parallel(self, paths: List[str]) -> List[Document]:
        if not paths:
            return []

        if isinstance(self.cfg.num_proc, str):
            nproc_cfg = (os.cpu_count() or 1) if self.cfg.num_proc == "max" else int(self.cfg.num_proc or 1)
        else:
            nproc_cfg = int(self.cfg.num_proc or 1)
        nproc = max(1, nproc_cfg)
        if os.name == "nt":
            nproc = 1

        byte_budget = max(1, int(self.cfg.prefetch_budget_mb or 1)) * 1024 * 1024
        batches, i, bid = [], 0, 0
        n = len(paths)
        step = max(1, int(self.cfg.io_batch_files or 1))
        while i < n:
            j = min(n, i + step)
            window = paths[i:j]
            items, _used = _read_bytes_with_budget(window, byte_budget)
            if not items:
                p = paths[i]
                try:
                    with open(p, "rb") as f:
                        items = [(p, f.read())]
                except Exception:
                    items = []
                j = i + 1
            batches.append((bid, items))
            bid += 1
            i = j

        if nproc == 1:
            out: List[Document] = []
            for _bid, file_items in batches:
                for path, b in file_items:
                    try:
                        out.extend(_decode_pdf_bytes(b, self.cfg.pdf_text_mode, path))
                    except Exception as e:
                        out.append(Document(page_content="", metadata={"source": path, "parse_error": True, "error": repr(e)}))
            return out

        import sys
        start_method = "fork" if sys.platform.startswith("linux") else "spawn"
        ctx = mp.get_context(start_method)
        in_q: mp.Queue = ctx.Queue(maxsize=max(2, int(self.cfg.io_batch_files or 1)))
        out_q: mp.Queue = ctx.Queue()

        workers = [ctx.Process(target=_worker, args=(in_q, out_q, self.cfg.pdf_text_mode)) for _ in range(nproc)]
        for w in workers:
            w.start()


        for b in batches:
            in_q.put(b)
        for _ in workers:
            in_q.put(None)

        num_batches = len(batches)
        got_batches = 0
        done_workers = 0
        results: dict[int, List[Document]] = {}
        while got_batches < num_batches or done_workers < nproc:
            item = out_q.get()
            if item is None:
                done_workers += 1
                continue
            batch_id, docs = item
            results[batch_id] = docs
            got_batches += 1

        for w in workers:
            w.join()

        ordered: List[Document] = []
        for k in range(num_batches):
            ordered.extend(results.get(k, []))
        return ordered

