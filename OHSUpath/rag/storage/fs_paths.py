# rag/storage/fs_paths.py

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FsLayout:
    base: Path
    index_dir: Path
    manifest_db: Path
    embed_cache_db: Path
    journal_log: Path
    lock_file: Path
    tmp_dir: Path

    @staticmethod
    def from_base(base: str | os.PathLike[str]) -> "FsLayout":
        b = Path(base).expanduser()
        return FsLayout(
            base=b,
            index_dir=b / "index",
            manifest_db=b / "manifest.sqlite",
            embed_cache_db=b / "embed_cache.sqlite",
            journal_log=b / "journal.log",
            lock_file=b / ".rag.lock",
            tmp_dir=b / "_tmp",
        )

def ensure_dirs(layout: FsLayout) -> None:
    layout.base.mkdir(parents=True, exist_ok=True)
    layout.index_dir.mkdir(parents=True, exist_ok=True)
    layout.tmp_dir.mkdir(parents=True, exist_ok=True)

__all__ = ["FsLayout", "ensure_dirs"]


