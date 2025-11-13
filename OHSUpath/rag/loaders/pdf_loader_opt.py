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

def _batch_generator(paths: List[str], byte_budget: int, step: int):
    """Streaming batch generator - prevents memory overflow with large file sets."""
    i, bid, n = 0, 0, len(paths)
    while i < n:
        j = min(n, i + step)
        window = paths[i:j]
        items, _used = _read_bytes_with_budget(window, byte_budget)
        if not items:
            # Single file fallback if budget exceeded
            p = paths[i]
            try:
                with open(p, "rb") as f:
                    items = [(p, f.read())]
            except Exception:
                items = []
            j = i + 1
        yield (bid, items)
        bid += 1
        i = j

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

        n_files = len(paths)
        # Logging for large datasets to help debug WSL2 stability
        if n_files > 1000:
            import sys
            print(f"[pdf_loader] Processing {n_files} PDFs with streaming batches to prevent memory overflow", file=sys.stderr)

        # Determine number of processes (allow "max" for full CPU utilization)
        if isinstance(self.cfg.num_proc, str):
            nproc_cfg = (os.cpu_count() or 1) if self.cfg.num_proc == "max" else int(self.cfg.num_proc or 1)
        else:
            nproc_cfg = int(self.cfg.num_proc or 1)
        nproc = max(1, nproc_cfg)
        if os.name == "nt":
            nproc = 1

        # Memory-aware batching: streaming generator prevents memory overflow with large datasets
        # For very large datasets (10K+ files), reduce batch size to minimize memory footprint
        byte_budget = max(1, int(self.cfg.prefetch_budget_mb or 1)) * 1024 * 1024
        step = max(1, int(self.cfg.io_batch_files or 1))

        # WSL2 stability: scale down for large datasets
        if n_files > 1000:
            byte_budget = min(byte_budget, 16 * 1024 * 1024)  # Cap at 16MB for large datasets (was 32MB)
            step = min(step, 2)  # Smaller batches (was 4)
            import sys
            print(f"[pdf_loader] Large dataset detected ({n_files} files): reduced batch size to {step} files, {byte_budget // (1024*1024)}MB budget", file=sys.stderr)

        # Single-process fallback
        if nproc == 1:
            out: List[Document] = []
            for _, file_items in _batch_generator(paths, byte_budget, step):
                for path, b in file_items:
                    try:
                        out.extend(_decode_pdf_bytes(b, self.cfg.pdf_text_mode, path))
                    except Exception as e:
                        out.append(Document(page_content="", metadata={"source": path, "parse_error": True, "error": repr(e)}))
            return out

        # Multi-process path with proper cleanup and streaming batches
        import sys
        start_method = "fork" if sys.platform.startswith("linux") else "spawn"
        ctx = mp.get_context(start_method)

        # Queue size: keep it bounded to prevent memory bloat with large datasets
        # For 10K+ files, we want to stream batches, not queue them all
        # CRITICAL: Smaller queues for WSL2 stability - prevents memory pressure/disconnects
        # For very large datasets, reduce queue size further
        if n_files > 5000:
            queue_size = max(2, min(nproc, 4))  # Minimal queues for huge datasets
        else:
            queue_size = max(2, min(nproc * 2, 8))  # Reduced from 16 to 8 for WSL2 stability
        in_q: mp.Queue = ctx.Queue(maxsize=queue_size)
        out_q: mp.Queue = ctx.Queue(maxsize=queue_size)  # Also limit output queue

        workers = []
        try:
            # Start worker processes
            workers = [ctx.Process(target=_worker, args=(in_q, out_q, self.cfg.pdf_text_mode)) for _ in range(nproc)]
            for w in workers:
                w.start()

            # Stream batches to workers using generator (prevents memory overflow)
            # Use a separate thread to feed the queue so we can collect results in parallel
            import threading
            batch_count = [0]  # Mutable container for thread communication

            def _producer():
                for b in _batch_generator(paths, byte_budget, step):
                    in_q.put(b)
                    batch_count[0] += 1
                # Send termination signals
                for _ in workers:
                    in_q.put(None)

            producer_thread = threading.Thread(target=_producer, daemon=True)
            producer_thread.start()

            # Collect results with timeout protection
            got_batches = 0
            done_workers = 0
            results: dict[int, List[Document]] = {}

            # Wait for producer to finish so we know final batch count
            # Use estimated_batches for progress, actual count from producer thread
            # CRITICAL: Shorter timeout for WSL2 - detect hangs faster and prevent system freeze
            # Adaptive timeout: longer for large datasets where each batch takes more time
            batch_timeout = 60 if n_files < 5000 else 180  # 1 min for small, 3 min for huge datasets
            while done_workers < nproc:
                try:
                    item = out_q.get(timeout=batch_timeout)
                    if item is None:
                        done_workers += 1
                        continue
                    batch_id, docs = item
                    results[batch_id] = docs
                    got_batches += 1
                except Exception as e:
                    import sys
                    print(f"[ERROR] Worker timeout or failure: {repr(e)}", file=sys.stderr)
                    print(f"[ERROR] Got {got_batches} batches, {done_workers} workers done", file=sys.stderr)
                    break

        finally:
            # CRITICAL: Proper cleanup prevents WSL2 zombie processes/disconnects
            # Ensure all workers are properly terminated
            for w in workers:
                if w.is_alive():
                    w.terminate()
            # Wait for termination
            for w in workers:
                w.join(timeout=3)  # Reduced timeout for faster cleanup
            # Force kill any remaining processes
            for w in workers:
                if w.is_alive():
                    import sys
                    print(f"[WARN] Force killing worker PID {w.pid}", file=sys.stderr)
                    w.kill()
                    w.join(timeout=1)  # Final cleanup
            # Close queues to release resources
            try:
                in_q.close()
                in_q.join_thread()
            except Exception:
                pass
            try:
                out_q.close()
                out_q.join_thread()
            except Exception:
                pass

        # Wait for producer thread to finish
        producer_thread.join(timeout=10)

        # Reconstruct ordered results using actual batch count
        ordered: List[Document] = []
        for k in range(batch_count[0]):
            ordered.extend(results.get(k, []))

        # Clear results dict and force garbage collection for WSL2 stability
        results.clear()
        import gc
        gc.collect()

        return ordered

