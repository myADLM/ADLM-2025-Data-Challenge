# rag/storage/journal.py

from __future__ import annotations

import os
import json
import time
import socket
import threading
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

from .fs_paths import FsLayout, ensure_dirs, interprocess_lock


_CFG = None


def _get_cfg():
    global _CFG
    if _CFG is None:
        from config import load_config

        _CFG = load_config()  # YAML + env overrides
    return _CFG


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    return obj


def _append_line_atomic(path: Path, line: str, *, fsync: bool = True) -> None:
    """
    Single append write using O_APPEND.
    One write = one line; with locking, lines won't interleave.
    """
    flags = os.O_CREAT | os.O_WRONLY | os.O_APPEND
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(os.fspath(path), flags, 0o666)
    try:
        os.write(fd, line.encode("utf-8"))
        if fsync:
            os.fsync(fd)
    finally:
        os.close(fd)


def journal_append(
    layout: FsLayout,
    event: str,
    data: Optional[dict[str, Any]] = None,
    *,
    ts: Optional[float] = None,
    lock: Optional[bool] = None,
    fsync: Optional[bool] = None,
    compact: Optional[bool] = None,
    max_record_bytes: Optional[int] = None,
) -> None:
    """
    Append one JSON line to the journal.
    Fields: ts, event, data, host, pid, tid.
    """
    if not isinstance(event, str) or not event:
        raise ValueError("event must be a non-empty string")

    cfg = _get_cfg()
    if lock is None:
        lock = cfg.journal.enable_lock
    if fsync is None:
        fsync = cfg.journal.fsync_default
    if compact is None:
        compact = cfg.journal.compact_json
    if max_record_bytes is None:
        max_record_bytes = cfg.journal.max_record_bytes

    ensure_dirs(layout)
    p = Path(layout.journal_log).expanduser()

    thr = threading.current_thread()
    try:
        tid_native = threading.get_native_id()
    except Exception:
        tid_native = threading.get_ident()
    rec = {
        "ts": float(ts if ts is not None else time.time()),
        "event": event,
        "data": _to_jsonable(data or {}),
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "tid": threading.current_thread().name,
        "tid_native": tid_native,
        "tid_name": threading.current_thread().name,
    }

    separators = (",", ":") if compact else None
    line = json.dumps(rec, ensure_ascii=False, separators=separators) + "\n"

    if max_record_bytes is not None and len(line.encode("utf-8")) > max_record_bytes:
        rec["data"] = {"_truncated": True}
        line = json.dumps(rec, ensure_ascii=False, separators=separators) + "\n"

    if lock:
        with interprocess_lock(
            layout.lock_file,
            timeout_s=cfg.lock.timeout_s,
            backoff_initial_s=cfg.lock.backoff_initial_s,
            backoff_max_s=cfg.lock.backoff_max_s,
        ):
            _append_line_atomic(p, line, fsync=fsync)
    else:
        _append_line_atomic(p, line, fsync=fsync)


def iter_journal(layout: FsLayout) -> Iterable[dict[str, Any]]:
    """
    Read the journal line by line.
    Invalid lines are skipped silently.
    """
    p = Path(layout.journal_log).expanduser()
    if not p.exists():
        return
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def rotate_journal(
    layout: FsLayout,
    *,
    max_bytes: Optional[int] = None,
    keep: Optional[int] = None,
) -> None:
    """
    Simple rotation: journal.log -> journal.log.1..N
    when size exceeds the limit.
    """
    cfg = _get_cfg()
    if max_bytes is None:
        max_bytes = cfg.journal.rotate_max_bytes
    if keep is None:
        keep = cfg.journal.rotate_keep

    p = Path(layout.journal_log).expanduser()
    if not p.exists() or p.stat().st_size < max_bytes:
        return

    with interprocess_lock(
        layout.lock_file,
        timeout_s=cfg.lock.timeout_s,
        backoff_initial_s=cfg.lock.backoff_initial_s,
        backoff_max_s=cfg.lock.backoff_max_s,
    ):
        if not p.exists() or p.stat().st_size < max_bytes:
            return
        oldest = p.with_name(p.name + f".{keep}")
        if oldest.exists():
            oldest.unlink(missing_ok=True)  # type: ignore[arg-type]
        for i in range(keep - 1, 0, -1):
            src = p.with_name(p.name + f".{i}")
            dst = p.with_name(p.name + f".{i+1}")
            if src.exists():
                src.replace(dst)
        p.replace(p.with_name(p.name + ".1"))
