# rag/cache/embed_cache.py

from __future__ import annotations
import os
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Union, Iterable, Optional, Tuple

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


def _build_schema(
    *,
    journal_mode: str,
    busy_timeout_ms: int,
    synchronous: str,
    table_name: str,
) -> str:
    jm, syn = _normalize_sqlite_opts(journal_mode, synchronous)
    bt = max(0, int(busy_timeout_ms))
    return f"""
PRAGMA journal_mode={jm};
PRAGMA busy_timeout={bt};
PRAGMA synchronous={syn};
CREATE TABLE IF NOT EXISTS {table_name}(
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL
);
""".strip()


@contextmanager
def _conn(db_path: PathLike):
    cfg = load_config()
    s_cfg = cfg.sqlite
    ecfg = cfg.embed_cache

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
                table_name=ecfg.table_name,
            )
        )
        yield con
    finally:
        con.close()


def _chunked(seq: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _max_vars(con: sqlite3.Connection, *, fallback: int, reserve: int) -> int:
    """
    Best-effort query of SQLite's max bind parameters.
    Falls back to a configurable default if unavailable.
    Reserve a few for safety (e.g., triggers/virtual tables).
    """
    try:
        row = con.execute("PRAGMA max_variable_number").fetchone()
        if row and row[0]:
            return max(1, int(row[0]) - int(reserve))
    except Exception:
        pass
    return int(fallback)

def _json_dumps(obj, *, ensure_ascii: bool, separators: Tuple[str, str]) -> str:
    return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators)


def get_many(db_path: PathLike, keys: List[str]) -> Dict[str, List[float]]:
    if not keys:
        return {}
    cfg = load_config().embed_cache
    out: Dict[str, List[float]] = {}
    with _conn(db_path) as con:
        batch_size = _max_vars(
            con,
            fallback=cfg.max_vars_fallback,
            reserve=cfg.reserve_bind_params,
        )
        if cfg.chunk_size_limit is not None:
            batch_size = max(1, min(batch_size, int(cfg.chunk_size_limit)))

        uniq_keys = list(dict.fromkeys(keys))
        placeholders_cache: Dict[int, str] = {}
        q_tmpl = f"SELECT k,v FROM {cfg.table_name} WHERE k IN ({{ph}})"

        for batch in _chunked(uniq_keys, batch_size):
            n = len(batch)
            if n not in placeholders_cache:
                placeholders_cache[n] = ",".join("?" * n)
            q = q_tmpl.format(ph=placeholders_cache[n])
            for k, v in con.execute(q, batch):
                out[k] = json.loads(v)
    return out


def put_many(db_path: PathLike, kv: Dict[str, List[float]]) -> None:
    if not kv:
        return
    cfg = load_config()
    ecfg = cfg.embed_cache
    with _conn(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.executemany(
                f"REPLACE INTO {ecfg.table_name}(k,v) VALUES(?,?)",
                (
                    (
                        k,
                        _json_dumps(
                            v,
                            ensure_ascii=ecfg.json_ensure_ascii,
                            separators=tuple(ecfg.json_separators),
                        ),
                    )
                    for k, v in kv.items()
                ),
            )
        except Exception:
            con.rollback()
            raise
        else:
            con.commit()
