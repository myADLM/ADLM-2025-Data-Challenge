# rag/cache/embed_cache.py

from __future__ import annotations
import os
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Union, Iterable

from config import load_config

PathLike = Union[str, os.PathLike[str]]


def _normalize_sqlite_opts(journal_mode: str, synchronous: str) -> tuple[str, str]:
    jm = str(journal_mode).upper()
    syn = str(synchronous).upper()
    jm_allowed = {"WAL", "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "OFF"}
    syn_allowed = {"OFF", "NORMAL", "FULL", "EXTRA"}
    if jm not in jm_allowed:
        jm = "WAL"
    if syn not in syn_allowed:
        syn = "NORMAL"
    return jm, syn


def _build_schema(*, journal_mode: str, busy_timeout_ms: int, synchronous: str) -> str:
    jm, syn = _normalize_sqlite_opts(journal_mode, synchronous)
    bt = max(0, int(busy_timeout_ms))
    return f"""
PRAGMA journal_mode={jm};
PRAGMA busy_timeout={bt};
PRAGMA synchronous={syn};
CREATE TABLE IF NOT EXISTS emb_cache(
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL
);
""".strip()


@contextmanager
def _conn(db_path: PathLike):
    cfg = load_config()
    s_cfg = cfg.sqlite

    p = Path(db_path).expanduser()
    if p.parent != p:
        p.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(
        os.fspath(p),
        timeout=float(s_cfg.connect_timeout_s),
        isolation_level=None,
    )
    try:
        con.executescript(
            _build_schema(
                journal_mode=s_cfg.journal_mode,
                busy_timeout_ms=s_cfg.busy_timeout_ms,
                synchronous=s_cfg.synchronous,
            )
        )
        yield con
    finally:
        con.close()


def _chunked(seq: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _max_vars(con: sqlite3.Connection) -> int:
    """
    Best-effort query of SQLite's max bind parameters.
    Falls back to a conservative default if unavailable.
    """
    try:
        row = con.execute("PRAGMA max_variable_number").fetchone()
        if row and row[0]:
            return max(1, int(row[0]) - 16)
    except Exception:
        pass
    return 900


def get_many(db_path: PathLike, keys: List[str]) -> Dict[str, List[float]]:
    if not keys:
        return {}
    out: Dict[str, List[float]] = {}
    with _conn(db_path) as con:
        batch_size = _max_vars(con)
        uniq_keys = list(dict.fromkeys(keys))
        for batch in _chunked(keys, batch_size):
            placeholders = ",".join("?" * len(batch))
            q = f"SELECT k,v FROM emb_cache WHERE k IN ({placeholders})"
            for k, v in con.execute(q, batch):
                out[k] = json.loads(v)
    return out


def put_many(db_path: PathLike, kv: Dict[str, List[float]]) -> None:
    if not kv:
        return
    with _conn(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.executemany(
                "REPLACE INTO emb_cache(k,v) VALUES(?,?)",
                (
                    (k, json.dumps(v, ensure_ascii=False, separators=(",", ":")))
                    for k, v in kv.items()
                ),
            )
        except Exception:
            con.rollback()
            raise
        else:
            con.commit()
