# rag/manifest_sqlite.py

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Union
from .types import FileMeta
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
CREATE TABLE IF NOT EXISTS files(
  path   TEXT PRIMARY KEY,
  size   INTEGER NOT NULL,
  mtime  REAL NOT NULL,
  sha256 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta(
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
        schema = _build_schema(
            journal_mode=s_cfg.journal_mode,
            busy_timeout_ms=s_cfg.busy_timeout_ms,
            synchronous=s_cfg.synchronous,
        )
        con.executescript(schema)
        yield con
    finally:
        con.close()

def load_all(db_path: PathLike) -> dict[str, FileMeta]:
    with _conn(db_path) as con:
        cur = con.execute("SELECT path,size,mtime,sha256 FROM files")
        return {
            path: FileMeta(path, size, mtime, sha256)
            for path, size, mtime, sha256 in cur
        }

def save_bulk(db_path: PathLike, files: dict[str, FileMeta]) -> None:
    with _conn(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute("DELETE FROM files")
            con.executemany(
                "INSERT INTO files(path,size,mtime,sha256) VALUES(?,?,?,?)",
                ((f.path, f.size, f.mtime, f.sha256) for f in files.values()),
            )
        except Exception:
            con.rollback()
            raise
        else:
            con.commit()
