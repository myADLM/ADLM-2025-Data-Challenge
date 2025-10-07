# rag/vectorstores/sparse_compact_daemon.py

from __future__ import annotations
import os
import time
import threading
from typing import Callable

from .bm25_shards import BM25ShardSet
from ..storage.fs_paths import FsLayout, interprocess_lock
from ..storage.journal import journal_append


_started_flag = False


def _latest_delta_mtime(root: str) -> float | None:
    import glob
    paths = sorted([p for p in glob.glob(os.path.join(root, "delta-*")) if os.path.isdir(p)])
    if not paths:
        return None
    return max(os.path.getmtime(p) for p in paths)


def start_sparse_compact_daemon(
    *,
    layout: FsLayout,
    backend: str,
    shards_root: str,
    collect_items: Callable[[], list[tuple[str, str]]],
    interval_s: int = 600,
    quiet_delay_s: int = 300,
):
    """
    Background thread: runs every interval_s seconds:
      - If there are delta-* dirs and the mtime of the latest delta is older
        than quiet_delay_s, run compaction: acquire a process lock, rebuild
        base, atomically switch the pointer, and clear deltas.
    """
    global _started_flag
    if _started_flag:
        return
    _started_flag = True

    def loop():
        root = os.path.abspath(shards_root)
        while True:
            try:
                time.sleep(max(5, int(interval_s)))
                last = _latest_delta_mtime(root)
                if last is None:
                    continue
                if (time.time() - last) < max(30, int(quiet_delay_s)):
                    continue

                # Avoid conflicts with foreground refresh/commit by taking a process lock
                with interprocess_lock(
                    layout.lock_file,
                    timeout_s=30.0,
                    backoff_initial_s=0.001,
                    backoff_max_s=0.05,
                ):
                    journal_append(layout, "SPARSE_COMPACT_START", {"root": root})
                    shardset = BM25ShardSet(root, backend=backend)

                    def _items():
                        return collect_items() or []

                    shardset.compact(_items, keep_prev_bases=1, remove_deltas=True)
                    journal_append(layout, "SPARSE_COMPACT_END", {"ok": True})
            except Exception as e:
                try:
                    journal_append(layout, "SPARSE_COMPACT_ERROR", {"error": repr(e)})
                except Exception:
                    pass

    t = threading.Thread(target=loop, name="sparse-compact-daemon", daemon=True)
    t.start()
