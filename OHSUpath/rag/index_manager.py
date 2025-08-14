# rag/index_manager.py

from __future__ import annotations

import os
import time
import fnmatch
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from config import load_config

try:
    from langchain.schema import Document
except Exception:
    from langchain_core.documents import Document

from .types import FileMeta, DiffResult, Chunk
from .manifest_sqlite import load_all, save_bulk
from .storage.fs_paths import FsLayout, ensure_dirs, interprocess_lock
from .storage.journal import journal_append
from .hashing import sha256_str
from .cache import embed_cache as cache


# ---------- helpers ----------

def _fast_stat(path: str) -> Tuple[int, float]:
    s = os.stat(path)
    return s.st_size, s.st_mtime

def _sha256_file(path: str, buf: int) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(buf)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def _stat_to_meta(path: str, size: int, mtime: float, sha256: Optional[str]) -> FileMeta:
    return FileMeta(path=os.path.abspath(path), size=size, mtime=mtime, sha256=sha256 or "")

def _diff_files_lazy(
    curr_paths: List[str],
    prev: Dict[str, FileMeta],
    *,
    hash_buf: int,
) -> Tuple[Dict[str, FileMeta], DiffResult]:
    """Build 'curr' with lazy sha256: only for added or size/mtime-changed files."""
    curr: Dict[str, FileMeta] = {}
    prev = prev or {}

    added: List[FileMeta] = []
    removed: List[FileMeta] = []
    modified: List[tuple[FileMeta, FileMeta]] = []

    prev_keys = set(prev.keys())
    curr_keys: Set[str] = set()

    # stat first (no hashing)
    stat_map: Dict[str, Tuple[int, float]] = {}
    for p in curr_paths:
        ap = os.path.abspath(p)
        curr_keys.add(ap)
        try:
            stat_map[ap] = _fast_stat(ap)
        except FileNotFoundError:
            continue

    # removed
    for k in (prev_keys - curr_keys):
        removed.append(prev[k])

    # added/modified
    for ap in curr_keys:
        size, mtime = stat_map[ap]
        prev_meta = prev.get(ap)
        if prev_meta is None:
            sha = _sha256_file(ap, hash_buf)
            fm = _stat_to_meta(ap, size, mtime, sha)
            curr[ap] = fm
            added.append(fm)
        else:
            if prev_meta.size != size or prev_meta.mtime != mtime:
                sha = _sha256_file(ap, hash_buf)
                fm = _stat_to_meta(ap, size, mtime, sha)
                curr[ap] = fm
                modified.append((prev_meta, fm))
            else:
                fm = _stat_to_meta(ap, size, mtime, prev_meta.sha256)
                curr[ap] = fm

    return curr, DiffResult(added=added, removed=removed, modified=modified)

def _meta_source(md: dict | None) -> Optional[str]:
    """Match chunker/source extraction priorities."""
    md = md or {}
    return md.get("source") or md.get("file_path") or md.get("path")

def _build_cache_key(text: str, model_name: str, normalize: bool, dim: Optional[int]) -> str:
    # include normalize + expected dim to avoid stale/incompatible cache hits
    base = f"{sha256_str(text)[:24]}|{sha256_str(model_name)[:16]}|{'1' if normalize else '0'}"
    if dim is not None:
        base += f"|d{int(dim)}"
    return base

def _is_dotpath(p: Path) -> bool:
    for part in p.parts:
        if part.startswith("."):
            return True
    return False

def _filter_paths(
    paths: List[str],
    *,
    include_globs: List[str],
    exclude_globs: List[str],
    ignore_dotfiles: bool,
    follow_symlinks: bool,
) -> List[str]:
    out: List[str] = []
    inc = [g for g in (include_globs or []) if g]
    exc = [g for g in (exclude_globs or []) if g]

    for p in paths:
        pp = Path(p)
        if not follow_symlinks and pp.is_symlink():
            continue
        if ignore_dotfiles and _is_dotpath(pp):
            continue

        posix = pp.as_posix()
        if inc:
            if not any(fnmatch.fnmatch(posix, g) for g in inc):
                continue
        if exc:
            if any(fnmatch.fnmatch(posix, g) for g in exc):
                continue

        out.append(p)
    return out

def _cfg_get(obj: Any, name: str, default: Any = None) -> Any:
    """Read config from either an object or a dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


# ---------- manager ----------

class IndexManager:
    """
    Orchestrates scan → diff → load → split → embed(+cache) → (LOCK) delete/upsert/persist → manifest → journal.
    Heavy work (I/O & compute) happens OUTSIDE the lock; only mutations are locked.
    """

    def __init__(
        self,
        layout: FsLayout,
        vector_index,
        embedder,
        loader,
        chunker,
        cfg: Any = None,
        *,
        yaml_path: str = "config.yaml",
        use_yaml: bool = True,
    ):
        if cfg is None:
            cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)
        self.layout = layout
        self.index = vector_index
        self.embedder = embedder
        self.loader = loader
        self.chunker = chunker
        self.cfg = cfg
        self._yaml_path = yaml_path
        self._use_yaml = use_yaml

    @classmethod
    def from_config(
        cls,
        layout: FsLayout,
        vector_index,
        embedder,
        loader,
        chunker,
        yaml_path: str = "config.yaml",
        use_yaml: bool = True
    ):
        return cls(
            layout, vector_index, embedder, loader, chunker,
            None, yaml_path=yaml_path, use_yaml=use_yaml
        )

    def reload_config(self, *, yaml_path: Optional[str] = None, use_yaml: Optional[bool] = None) -> None:
        """
        Hot-reload configuration.
        """
        yp = yaml_path if yaml_path is not None else self._yaml_path
        uy = use_yaml if use_yaml is not None else self._use_yaml
        self.cfg = load_config(yaml_path=yp, use_yaml=uy)

    # --- bootstrap ---

    def bootstrap(self, data_dir: str, exts: List[str] | None) -> Dict[str, FileMeta]:
        ensure_dirs(self.layout)
        self.index.load_or_init(str(self.layout.index_dir))
        return load_all(str(self.layout.manifest_db))

    # --- refresh ---

    def refresh(self, data_dir: str, exts: List[str] | None, prev: Dict[str, FileMeta]) -> Dict[str, FileMeta]:
        """
        Returns the new manifest map (path -> FileMeta).
        """
        ensure_dirs(self.layout)

        m = _cfg_get(self.cfg, "manager", None)
        enable_cache = bool(_cfg_get(m, "enable_cache", True))
        enable_journal = bool(_cfg_get(m, "enable_journal", True))
        hash_buf = int(_cfg_get(m, "hash_block_bytes", 1024 * 1024))
        include_globs = list(_cfg_get(m, "include_globs", []) or [])
        exclude_globs = list(_cfg_get(m, "exclude_globs", []) or [])
        follow_symlinks = bool(_cfg_get(m, "follow_symlinks", False))
        ignore_dotfiles = bool(_cfg_get(m, "ignore_dotfiles", True))

        t0 = time.time()
        if enable_journal:
            journal_append(self.layout, "BEGIN_REFRESH", {"data_dir": data_dir})

        try:
            # 1) discover (loader supports exts=None)
            paths = list(self.loader.discover(data_dir, exts))
            paths = _filter_paths(
                paths,
                include_globs=include_globs,
                exclude_globs=exclude_globs,
                ignore_dotfiles=ignore_dotfiles,
                follow_symlinks=follow_symlinks,
            )

            # 2) diff with lazy hashing
            curr, d = _diff_files_lazy(paths, prev, hash_buf=hash_buf)

            # 3) delete set (by file path)
            rm_paths: Set[str] = {f.path for f in d.removed} | {new.path for _, new in d.modified}

            # 4) load new/modified (outside lock)
            add_paths: List[str] = [f.path for f in d.added] + [new.path for _, new in d.modified]
            docs: List[Document] = []
            if add_paths:
                if hasattr(self.loader, "load_many_parallel"):
                    docs = self.loader.load_many_parallel(add_paths)
                else:
                    for p in add_paths:
                        docs.extend(self.loader.load(p))

            # 5) split (outside lock)
            chunks: List[Chunk] = self.chunker.split(docs) if docs else []

            # 6) embed (+ optional cache)
            vecs: List[List[float]] = []
            if chunks:
                model_name = getattr(self.embedder, "model_name", type(self.embedder).__name__)
                # expected dim: cfg.embedding.embedding_dim > embedder.embedding_dim > None
                embedding_cfg = _cfg_get(self.cfg, "embedding", None)
                expected_dim = _cfg_get(embedding_cfg, "embedding_dim", None)
                if expected_dim is None:
                    expected_dim = getattr(self.embedder, "embedding_dim", None)
                normalize = bool(_cfg_get(getattr(self.embedder, "cfg", None), "normalize", False))

                if enable_cache:
                    keys = [_build_cache_key(c.content, model_name, normalize, expected_dim) for c in chunks]
                    hits = cache.get_many(str(self.layout.embed_cache_db), keys)
                    miss_idx = [i for i, k in enumerate(keys) if k not in hits]
                    if miss_idx:
                        miss_texts = [chunks[i].content for i in miss_idx]
                        new_vecs = self.embedder.embed(miss_texts)
                        if len(new_vecs) != len(miss_idx):
                            raise ValueError(f"Embedder returned {len(new_vecs)} vectors for {len(miss_idx)} texts.")
                        if expected_dim is not None and new_vecs and len(new_vecs[0]) != int(expected_dim):
                            raise ValueError(f"Embedding dim mismatch: got {len(new_vecs[0])}, expected {expected_dim}")
                        cache.put_many(
                            str(self.layout.embed_cache_db),
                            {keys[i]: new_vecs[j] for j, i in enumerate(miss_idx)},
                        )
                        for j, i in enumerate(miss_idx):
                            hits[keys[i]] = new_vecs[j]
                    vecs = [hits[k] for k in keys]
                else:
                    # no cache path
                    texts = [c.content for c in chunks]
                    vecs = self.embedder.embed(texts)
                    if expected_dim is not None and vecs and len(vecs[0]) != int(expected_dim):
                        raise ValueError(f"Embedding dim mismatch: got {len(vecs[0])}, expected {expected_dim}")

            # 7) commit stage (lock): delete → upsert → persist → manifest
            lock_cfg = _cfg_get(self.cfg, "lock", None)
            lock_kwargs = dict(
                timeout_s=float(_cfg_get(lock_cfg, "timeout_s", 30.0)),
                backoff_initial_s=float(_cfg_get(lock_cfg, "backoff_initial_s", 0.001)),
                backoff_max_s=float(_cfg_get(lock_cfg, "backoff_max_s", 0.05)),
            )
            with interprocess_lock(str(self.layout.lock_file), **lock_kwargs):
                # delete by sources (prefer public API if present)
                if rm_paths:
                    if hasattr(self.index, "delete_by_sources"):
                        self.index.delete_by_sources(rm_paths)
                    else:
                        to_delete: List[str] = []
                        ds = getattr(self.index, "_docstore", None)
                        dd = getattr(ds, "_dict", None)
                        if isinstance(dd, dict):
                            for cid, doc in dd.items():
                                src = _meta_source(getattr(doc, "metadata", None))
                                if src in rm_paths:
                                    to_delete.append(cid)
                        if to_delete:
                            self.index.delete_by_chunk_ids(to_delete)

                # upsert
                if chunks:
                    if len(chunks) != len(vecs):
                        raise ValueError(f"chunks ({len(chunks)}) and vectors ({len(vecs)}) length mismatch.")
                    self.index.upsert(chunks, vecs)

                # persist index + manifest
                self.index.persist_atomic(str(self.layout.index_dir))
                save_bulk(str(self.layout.manifest_db), curr)

            if enable_journal:
                journal_append(
                    self.layout,
                    "END_REFRESH",
                    {
                        "ok": True,
                        "added": len(d.added),
                        "removed": len(d.removed),
                        "modified": len(d.modified),
                        "t_ms": int((time.time() - t0) * 1000),
                    },
                )
            return curr

        except Exception as e:
            if enable_journal:
                journal_append(
                    self.layout,
                    "END_REFRESH",
                    {"ok": False, "error": repr(e), "t_ms": int((time.time() - t0) * 1000)},
                )
            raise
