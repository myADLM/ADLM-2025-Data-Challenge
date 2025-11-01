# rag/vectorstores/bm25_shards.py

from __future__ import annotations
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict

from .bm25_store import BM25SparseIndex
from ..storage.fs_paths import atomic_write_text


def _now_tag() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.localtime())


def _minmax_norm(pairs: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    if not pairs:
        return pairs
    vs = [s for _, s in pairs]
    lo, hi = min(vs), max(vs)
    span = (hi - lo) or 1.0
    return [(i, (s - lo) / span) for i, s in pairs]


class BM25ShardSet:
    """
    Directory layout (under <index_dir>/sparse_shards/):
      - CURRENT                  # text file pointing to active base dir, e.g., base-20250930-123456
      - base-YYYYmmdd-HHMMSS/    # base shards
      - delta-YYYYmmdd-HHMMSS/   # incremental shards (there can be multiple)

    Query: merge top-k from CURRENT base and all deltas, apply one MinMax normalization, then fuse.
    """

    def __init__(self, root_dir: str | os.PathLike[str], backend: str = "bm25s"):
        self.root = Path(root_dir).expanduser()
        self.backend = (backend or "bm25s").lower()
        self._cache: Dict[str, BM25SparseIndex] = {}  # dir name -> loaded index

    # ---------- layout helpers ----------
    @property
    def current_path(self) -> Path:
        return self.root / "CURRENT"

    def _current_base_name(self) -> Optional[str]:
        if not self.current_path.exists():
            return None
        try:
            return self.current_path.read_text(encoding="utf-8").strip() or None
        except Exception:
            return None

    def _base_dirs(self) -> List[Path]:
        return sorted([p for p in self.root.glob("base-*") if p.is_dir()])

    def _delta_dirs(self) -> List[Path]:
        return sorted([p for p in self.root.glob("delta-*") if p.is_dir()])

    def _load(self, d: Path) -> Optional[BM25SparseIndex]:
        key = d.name
        if key in self._cache:
            return self._cache[key]
        try:
            idx = BM25SparseIndex.load(os.fspath(d))
            self._cache[key] = idx
            return idx
        except Exception:
            return None

    # ---------- lifecycle ----------
    def ensure_base(self, items_supplier) -> None:
        """
        If CURRENT is missing or the base it points to does not exist,
        rebuild a full base-<ts> using items_supplier() and atomically switch to it.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        name = self._current_base_name()
        if name and (self.root / name).is_dir():
            return
        items: List[Tuple[str, str]] = items_supplier() or []
        base_name = f"base-{_now_tag()}"
        base_dir = self.root / base_name
        base_dir.mkdir(parents=True, exist_ok=True)

        idx = BM25SparseIndex(backend=self.backend)
        idx.build(items)
        idx.save(os.fspath(base_dir))

        atomic_write_text(self.root, self.current_path, base_name, encoding="utf-8")
        self._cache.clear()  # let the new base be lazily loaded next time

    def add_delta(self, items: List[Tuple[str, str]]) -> Optional[str]:
        """
        Write a new delta directory for the incremental (added/modified) chunks.
        Return the directory name.
        """
        if not items:
            return None
        self.root.mkdir(parents=True, exist_ok=True)
        dname = f"delta-{_now_tag()}"
        ddir = self.root / dname
        ddir.mkdir(parents=True, exist_ok=True)

        idx = BM25SparseIndex(backend=self.backend)
        idx.build(items)
        idx.save(os.fspath(ddir))

        # Put it into the in-memory cache (immediately visible for search)
        self._cache[dname] = idx
        return dname

    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Merge results from CURRENT base and all deltas (apply MinMax normalization once).
        """
        if not query or k <= 0:
            return []
        cur = self._current_base_name()
        shards: List[Path] = []
        if cur and (self.root / cur).is_dir():
            shards.append(self.root / cur)
        shards.extend(self._delta_dirs())

        merged: Dict[str, float] = {}
        for d in shards:
            idx = self._load(d)
            if not idx:
                continue
            try:
                hits = idx.search(query, k=k)
            except Exception:
                continue
            for cid, sc in hits:
                if not cid:
                    continue
                # For the same id across shards, keep the max score
                if cid not in merged or sc > merged[cid]:
                    merged[cid] = sc

        pairs = list(merged.items())
        pairs = _minmax_norm(pairs)
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:k]

    def compact(
        self,
        items_supplier,
        *,
        keep_prev_bases: int = 1,
        remove_deltas: bool = True,
    ) -> Optional[str]:
        """
        Compact all deltas into a new base:
          1) Rebuild base-<ts> using items_supplier().
          2) Atomically switch the CURRENT pointer.
          3) Optional: remove all delta-*; clean up old bases (keep keep_prev_bases latest).
        """
        items: List[Tuple[str, str]] = items_supplier() or []
        if not items:
            return None
        self.root.mkdir(parents=True, exist_ok=True)
        base_name = f"base-{_now_tag()}"
        base_dir = self.root / base_name
        base_dir.mkdir(parents=True, exist_ok=True)

        idx = BM25SparseIndex(backend=self.backend)
        idx.build(items)
        idx.save(os.fspath(base_dir))

        # Atomic switch of CURRENT
        atomic_write_text(self.root, self.current_path, base_name, encoding="utf-8")
        self._cache.clear()

        # Clean up deltas
        if remove_deltas:
            for d in self._delta_dirs():
                try:
                    for p in d.glob("*"):
                        p.unlink(missing_ok=True)  # type: ignore[arg-type]
                    d.rmdir()
                except Exception:
                    pass

        # Clean up old bases (keep the most recent keep_prev_bases)
        bases = self._base_dirs()
        if keep_prev_bases is not None and keep_prev_bases >= 0 and len(bases) > keep_prev_bases:
            victims = bases[:-keep_prev_bases]
            for b in victims:
                try:
                    for p in b.glob("*"):
                        p.unlink(missing_ok=True)  # type: ignore[arg-type]
                    b.rmdir()
                except Exception:
                    pass

        return base_name
