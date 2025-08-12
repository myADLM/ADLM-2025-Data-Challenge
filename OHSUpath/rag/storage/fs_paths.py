# rag/storage/fs_paths.py

import os
import tempfile
import contextlib
import stat as _stat
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


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


@contextlib.contextmanager
def interprocess_lock(lock_path: str | os.PathLike[str]) -> Iterator[None]:
    lp = Path(lock_path).expanduser()
    lp.parent.mkdir(parents=True, exist_ok=True)

    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(os.fspath(lp), flags, 0o666)

    try:
        if os.name == "nt":
            import msvcrt
            try:
                st = os.stat(lp)
                if st.st_size == 0:
                    os.write(fd, b"\0")
            except FileNotFoundError:
                pass
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            except OSError as e:
                raise RuntimeError(f"failed to acquire windows lock: {e}") from e
        else:
            try:
                import fcntl
            except ImportError:
                fcntl = None
            if fcntl is not None:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX)
                except OSError as e:
                    raise RuntimeError(f"failed to acquire posix lock: {e}") from e
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                with contextlib.suppress(Exception):
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                with contextlib.suppress(Exception):
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            with contextlib.suppress(Exception):
                os.close(fd)




def atomic_write_text(
    dirpath: str | os.PathLike[str],
    final_path: str | os.PathLike[str],
    text: str,
    *,
    encoding: str = "utf-8",
    preserve_mode: bool = False,
) -> None:
    d = Path(dirpath).expanduser()
    dst = Path(final_path).expanduser()
    d.mkdir(parents=True, exist_ok=True)

    old_mode = None
    try:
        st = dst.stat()
        old_mode = st.st_mode
    except FileNotFoundError:
        pass

    try:
        same_dev = os.stat(d).st_dev == os.stat(dst.parent).st_dev
    except FileNotFoundError:
        dst.parent.mkdir(parents=True, exist_ok=True)
        same_dev = False
    write_dir = d if same_dev else dst.parent

    tmp_path = None
    with tempfile.NamedTemporaryFile(
        mode="w", dir=os.fspath(write_dir), delete=False, encoding=encoding
    ) as t:
        t.write(text)
        t.flush()
        os.fsync(t.fileno())
        tmp_path = t.name

    try:
        os.replace(tmp_path, os.fspath(dst))
    except Exception as e:
        if (
            isinstance(e, PermissionError)
            and os.name == "nt"
            and preserve_mode
            and old_mode is not None
            and (old_mode & _stat.S_IWRITE) == 0
        ):
            try:
                with contextlib.suppress(Exception):
                    os.chmod(dst, old_mode | _stat.S_IWRITE)
                os.replace(tmp_path, os.fspath(dst))
            except Exception:
                with contextlib.suppress(Exception):
                    os.remove(tmp_path)
                raise e
        else:
            with contextlib.suppress(Exception):
                os.remove(tmp_path)
            raise


    def _fsync_dir(p: Path) -> None:
        if hasattr(os, "O_DIRECTORY"):
            with contextlib.suppress(Exception):
                dir_fd = os.open(os.fspath(p), os.O_DIRECTORY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)

    _fsync_dir(dst.parent)
    if write_dir != dst.parent:
        _fsync_dir(write_dir)


    if preserve_mode and old_mode is not None:
        with contextlib.suppress(Exception):
            os.chmod(dst, old_mode)

