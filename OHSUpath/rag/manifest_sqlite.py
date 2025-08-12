# rag/manifest_sqlite.py

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Union
from .types import FileMeta

PathLike = Union[str, os.PathLike[str]]

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=30000;
PRAGMA synchronous=NORMAL;
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
"""

@contextmanager
def _conn(db_path: PathLike):
    p = Path(db_path).expanduser()
    if p.parent != p:
        p.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(os.fspath(p), timeout=30.0)
    try:
        con.executescript(SCHEMA)
        yield con
    finally:
        con.close()


def load_all(db_path: PathLike) -> dict[str, FileMeta]:
    with _conn(db_path) as con:
        cur = con.execute("SELECT path,size,mtime,sha256 FROM files")
        return {path: FileMeta(path, size, mtime, sha256)
                for path, size, mtime, sha256 in cur}

def save_bulk(db_path: PathLike, files: dict[str, FileMeta]) -> None:
    with _conn(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute("DELETE FROM files")
            con.executemany(
                "INSERT INTO files(path,size,mtime,sha256) VALUES(?,?,?,?)",
                ((f.path, f.size, f.mtime, f.sha256) for f in files.values())
            )
        except Exception:
            con.rollback()
            raise
        else:
            con.commit()
