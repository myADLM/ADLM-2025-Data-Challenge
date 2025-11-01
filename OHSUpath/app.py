# app.py

from __future__ import annotations

# CRITICAL: Set environment variables and multiprocessing BEFORE any other imports
import os
import sys

# Set essential environment variables before importing any other modules
# These suppress warnings and configure GPU usage
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Use fork on Linux/WSL2 for performance (faster than spawn, shares memory efficiently)
import multiprocessing as _mp
if sys.platform.startswith("linux"):
    try:
        _mp.set_start_method("fork", force=False)
    except RuntimeError:
        pass  # Already set
import streamlit as st
import shutil
from pathlib import Path
import datetime as dt
from sqlalchemy import desc
from sqlmodel import Session, select, SQLModel
from config import load_config
from rag.pipeline import RagPipeline
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from net.api.db import engine
from net.api.models import User, Conversation, Message, LoginEvent

# LangChain callback (some versions expose it under langchain_core)
try:
    from langchain_core.callbacks import BaseCallbackHandler
except Exception:  # pragma: no cover
    from langchain.callbacks.base import BaseCallbackHandler  # type: ignore

# --- DB engine and models (reuse the FastAPI layer so we share one database) ---
try:
    from net.api.db import engine, init_db
    from net.api.models import User, Conversation, Message, LoginEvent
    from net.api.security import hash_password
except Exception:  # pragma: no cover
    # Fallback import path when cwd differs
    from OHSUpath.net.api.db import engine  # type: ignore

    try:
        from OHSUpath.net.api.db import init_db  # type: ignore
    except Exception:
        init_db = None  # type: ignore
    from OHSUpath.net.api.models import User, Conversation, Message, LoginEvent  # type: ignore
    from OHSUpath.net.api.security import hash_password  # type: ignore


# ------------------------------------------------------------
# CONFIGURATION MODE SWITCH
# True  = Use YAML + env variables + defaults in config.py
# False = Use ONLY env variables + defaults in config.py
# ------------------------------------------------------------
USE_YAML_CONFIG_DEFAULT: bool = False   # True = use YAML, False = skip YAML


# ------------------------------------------------------------------------------
# LangChain prompt inspector
# ------------------------------------------------------------------------------
class PromptSpy(BaseCallbackHandler):
    """Collect prompts, params, and context for auditing."""

    def __init__(self):
        self.text_prompts: list[str] = []
        self.chat_prompts: list[list[object]] = []
        self.params: dict = {}

    def on_llm_start(self, _serialized, prompts, **kwargs):
        if prompts:
            self.text_prompts.extend(prompts)
        self.params = kwargs.get("invocation_params", self.params)

    def on_chat_model_start(self, _serialized, messages, **kwargs):
        if messages:
            self.chat_prompts.extend(messages)
        self.params = kwargs.get("invocation_params", self.params)


def render_prompt_spy(spy: PromptSpy, res: dict):
    """Expandable panel with prompt, params, and top context chunks."""
    with st.expander("What we sent to the LLM (prompt + context)", expanded=False):
        if spy.text_prompts:
            for i, p in enumerate(spy.text_prompts, 1):
                st.markdown(f"**Prompt {i}**")
                st.code(p)

        if spy.chat_prompts:
            for ri, run_msgs in enumerate(spy.chat_prompts, 1):
                st.markdown(f"**Chat Run {ri}**")
                for mi, m in enumerate(run_msgs, 1):
                    role = (
                        getattr(m, "type", None)
                        or getattr(m, "role", None)
                        or m.__class__.__name__
                    )
                    content = getattr(m, "content", "")
                    st.markdown(f"- **{mi}. {role}**")
                    st.code(content)
        if not spy.text_prompts and not spy.chat_prompts:
            st.info(
                "No prompt was intercepted from callbacks (expected if your chain/provider doesn't propagate)."
            )
        if spy.params:
            st.markdown("**LLM Params**")
            st.json(spy.params)
        docs = res.get("source_documents") or []
        if docs:
            st.markdown("**Context Chunks (top)**")
            for i, d in enumerate(docs[:5], 1):
                src = d.metadata.get("source")
                page = d.metadata.get("page_number", d.metadata.get("page"))
                st.markdown(f"**{i}.** `{src}` (page {page})")
                text = d.page_content or ""
                st.write(text[:800] + ("..." if len(text) > 800 else ""))
                st.caption(str(d.metadata))
                st.markdown("---")


# ------------------------------------------------------------------------------
# RAG index helpers
# ------------------------------------------------------------------------------
def clear_index(pipe: RagPipeline):
    """Best-effort cleanup of the index dir and manifest DB."""
    try:
        shutil.rmtree(pipe.layout.index_dir, ignore_errors=True)
    except Exception:
        pass
    man = pipe.layout.manifest_db
    if man.exists():
        try:
            man.unlink()
        except Exception:
            pass


def ensure_index(
    pipe: RagPipeline, *, force_clean: bool = False, ui: dict | None = None
):
    """
    Drive indexing/refresh with a progress UI.

    Updates the custom "Progress" card:
      - ui["phase"]: st.empty() - current phase text (indexing/splitting/embedding)
      - ui["bar"]:   st.progress - overall progress
      - ui["log"]:   st.empty() - multiline details (rendered only when expanded)

    Also persists to session_state so the card keeps state across reruns.
    """
    ui = ui or {}
    phase_ph = ui.get("phase")
    bar_ph = ui.get("bar")
    log_ph = ui.get("log")

    # --- Ensure UI state is ready BEFORE any heavy work/possible errors ---
    st.session_state.setdefault("index_phase", "starting...")
    st.session_state.setdefault("index_pct", 0)
    st.session_state.setdefault("index_logs", [])
    st.session_state.setdefault("index_summary", "")

    # Initialize visible widgets
    if phase_ph:
        phase_ph.markdown(f"**{st.session_state.index_phase}**")
    bar_handle = bar_ph.progress(st.session_state.index_pct if bar_ph else 0)

    # Phase labels and weights for overall progress
    label_map = {
        "discover": "scanning...",
        "diff": "scanning...",
        "load": "indexing...",
        "split": "splitting...",
        "embed": "embedding...",
        "commit": "committing...",
    }
    weights = {
        "discover": 0.05,
        "diff": 0.05,
        "load": 0.20,
        "split": 0.20,
        "embed": 0.40,
        "commit": 0.10,
    }
    seen: set[str] = set()

    # Throttle UI updates to ~5 updates/sec (every 200ms)
    import time
    last_update_time = {"time": 0}
    UPDATE_INTERVAL = 0.2

    # If rerun occurs within one session, we recompute pct from seen for simplicity
    def pct() -> int:
        return int(sum(weights[p] for p in seen if p in weights) * 100)

    def render_logs():
        if log_ph:
            # Render last 400 lines to keep the DOM light
            log_ph.text("\n".join(st.session_state.index_logs[-400:]))

    def push(line: str):
        st.session_state.index_logs.append(line)
        render_logs()

    def bump(base: str):
        if base in weights and base not in seen:
            seen.add(base)
            cur = min(pct(), 100)
            st.session_state.index_pct = cur
            bar_handle.progress(cur)

    if force_clean:
        push(f"[info] Rebuilding index under: {pipe.layout.index_dir.parent}")

    # Fast path: if not force_clean, check if we can skip reindexing entirely
    if not force_clean:
        try:
            from rag.manifest_sqlite import load_all
            prev = load_all(str(pipe.layout.manifest_db))

            # Quick check: discover files and compare counts
            from rag.loaders.pdf_loader_opt import PdfLoaderOptimized
            if hasattr(pipe.loader, 'discover'):
                current_files = list(pipe.loader.discover(pipe.layout.data_dir, pipe.layout.exts))
            else:
                current_files = []

            # If counts match, do a quick hash check on a sample
            if len(current_files) == len(prev):
                # Bootstrap to load index
                prev = pipe.bootstrap()

                # Now check if files actually changed
                push("[info] Checking for changes...")
                from rag.index_manager import _diff_files_lazy
                m_cfg = pipe.cfg.manager if hasattr(pipe.cfg, 'manager') else None
                hash_buf = int(m_cfg.hash_block_bytes if m_cfg and hasattr(m_cfg, 'hash_block_bytes') else 1024 * 1024)
                curr, diff_result = _diff_files_lazy(current_files, prev, hash_buf=hash_buf)

                # If nothing changed, skip directly to complete
                if not diff_result.added and not diff_result.removed and not diff_result.modified:
                    push("[OK] No changes detected. Index is up to date.")
                    st.session_state.index_phase = "complete"
                    st.session_state.index_pct = 100
                    if phase_ph:
                        phase_ph.markdown("**complete**")
                    bar_handle.progress(100)
                    st.session_state.index_summary = f"Index up to date. {len(prev)} files in manifest."
                    return prev
        except Exception as e:
            # Fall back to normal path if fast check fails
            push(f"[info] Fast check failed ({repr(e)}), running full refresh...")

    # Normal path: bootstrap and run full pipeline
    try:
        prev = pipe.bootstrap()
    except RuntimeError as e:
        if "Index meta mismatch" in str(e):
            push("[warn] Index meta mismatch. Cleaning index + manifest, rebuilding...")
            clear_index(pipe)
            prev = pipe.bootstrap()
        else:
            st.session_state.index_phase = "error"
            if phase_ph:
                phase_ph.markdown("**error**")
            st.session_state.index_pct = 100
            bar_handle.progress(100)
            push(f"[error] {repr(e)}")
            raise

    # refresh with progress
    try:

        def on_progress(event: str, **kw):
            """
            Progress event contract (emitted by IndexManager.refresh):
            - '{phase}_start' -> phase text + log
            - '{phase}_progress' -> update current/total display
            - '{phase}_done'  -> log + bump progress
            - 'discover'/'diff' -> treat as completed phases
            - 'refresh_error' -> error log
            """
            base = event.replace("_start", "").replace("_done", "").replace("_progress", "")

            if event.endswith("_start"):
                # Phase start: set phase label and initialize counters
                st.session_state.index_phase = label_map.get(base, base)
                current = kw.get("current", 0)
                total = kw.get("total", 0)
                st.session_state[f"{base}_current"] = current
                st.session_state[f"{base}_total"] = total

                # Update phase label with counts if available
                if total > 0:
                    phase_text = f"{st.session_state.index_phase} ({current:,} / {total:,})"
                    # Update progress bar at phase start
                    if current > 0:
                        start_pct = int((current / total) * 100)
                        st.session_state.index_pct = start_pct
                        bar_handle.progress(start_pct)
                else:
                    phase_text = st.session_state.index_phase

                if phase_ph:
                    phase_ph.markdown(f"**{phase_text}**")
                push(f"- {base}... {kw}")

            elif event.endswith("_progress"):
                # Granular progress update: update current/total display
                current = kw.get("current", 0)
                total = kw.get("total", 0)
                cached = kw.get("cached", 0)

                # Always update session state (this is the source of truth)
                st.session_state[f"{base}_current"] = current
                st.session_state[f"{base}_total"] = total
                if cached > 0:
                    st.session_state[f"{base}_cached"] = cached

                # Throttle UI updates to ~10 updates/sec based on wall-clock time
                current_time = time.time()
                time_since_last = current_time - last_update_time["time"]
                is_final = (current == total and total > 0)

                # Update UI if: enough time passed OR it's the final update
                if time_since_last >= UPDATE_INTERVAL or is_final:
                    last_update_time["time"] = current_time

                    # Read current state (may have advanced since this callback was queued)
                    display_current = st.session_state.get(f"{base}_current", current)
                    display_total = st.session_state.get(f"{base}_total", total)

                    # Build progress text - show file counts (current/total are already file counts)
                    if display_total > 0:
                        phase_text = f"{label_map.get(base, base)} ({display_current:,} / {display_total:,})"
                    else:
                        phase_text = label_map.get(base, base)

                    if phase_ph:
                        phase_ph.markdown(f"**{phase_text}**")

                    # Update progress bar - based purely on file count progress
                    # Simple: current files / total files = percentage
                    if display_total > 0:
                        # Direct percentage: files processed / total files
                        total_pct = int((display_current / display_total) * 100)
                        total_pct = min(total_pct, 99)  # Cap at 99% until complete

                        st.session_state.index_pct = total_pct
                        bar_handle.progress(total_pct)

            elif event.endswith("_done"):
                # Phase complete: use cached file counts from session state
                # (event may contain chunk counts, but we want file counts for display)
                current = st.session_state.get(f"{base}_current", 0)
                total = st.session_state.get(f"{base}_total", 0)

                # Update final phase text and progress bar
                if total > 0:
                    phase_text = f"{label_map.get(base, base)} ({current:,} / {total:,})"
                    if phase_ph:
                        phase_ph.markdown(f"**{phase_text}**")
                    # Update progress bar based on file count
                    done_pct = int((current / total) * 100)
                    done_pct = min(done_pct, 99)  # Cap at 99% until all phases complete
                    st.session_state.index_pct = done_pct
                    bar_handle.progress(done_pct)

                push(f"[OK] {base} done. {kw}")
                seen.add(base)  # Mark phase as complete

            elif event in ("discover", "diff"):
                push(f"[OK] {base}. {kw}")
                bump(base)

            elif event == "refresh_error":
                push(f"[ERROR] {kw.get('error')}")

            else:
                push(f"- {event}: {kw}")

        curr = pipe.refresh(prev, progress=on_progress)
    except Exception as e:  # pragma: no cover
        st.session_state.index_phase = "error"
        if phase_ph:
            phase_ph.markdown("**error**")
        st.session_state.index_pct = 100
        bar_handle.progress(100)
        push(f"[error] {repr(e)}")
        raise
    else:
        st.session_state.index_phase = "complete"
        st.session_state.index_pct = 100
        bar_handle.progress(100)
        if phase_ph:
            phase_ph.markdown("**complete**")
        st.session_state.index_summary = f"Indexing complete ({len(curr)} files)."
        push(f"[ok] {st.session_state.index_summary}")
        return curr


def clear_project_artifacts(pipe: RagPipeline):
    """
    Clean up regenerable artifacts:
      - Index directory + manifest (via _clear_index)
      - Entire .rag_store (only if it lives under the project root and the name
        looks like a vector-store directory)
      - Top-level .pytest_cache
      - All __pycache__ directories and *.pyc files
    Does NOT touch: source code, data/, minidata/, config
    """
    root = Path(__file__).resolve().parent

    # 1) index + manifest
    clear_index(pipe)

    # 2) .rag_store
    try:
        store_dir = Path(pipe.layout.index_dir).parent
        store_dir_res = store_dir.resolve()
        root_res = root.resolve()
        safe_names = {".rag_store", "rag_store", ".vectorstore", "indexes"}
        is_under_project = root_res in store_dir_res.parents
        looks_like_store = store_dir_res.name in safe_names
        if is_under_project and looks_like_store and store_dir_res.is_dir():
            shutil.rmtree(store_dir_res, ignore_errors=True)
    except Exception:
        pass

    # 3) .pytest_cache
    shutil.rmtree(root / ".pytest_cache", ignore_errors=True)

    # 4) __pycache__ and *.pyc
    try:
        for p in root.rglob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)
        for p in root.rglob("*.pyc"):
            try:
                p.unlink()
            except Exception:
                pass
    except Exception:
        pass


# ------------------------------------------------------------------------------
# DB bootstrap (when the API has not been started yet)
# ------------------------------------------------------------------------------
def ensure_db_ready():
    """
    If net.api.db.init_db exists, use it.
    Otherwise set SQLite pragmas and create tables from SQLModel metadata.
    """
    if callable(init_db):
        init_db()
        return

    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
        conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
    SQLModel.metadata.create_all(engine)


# ------------------------------------------------------------------------------
# Session init
# ------------------------------------------------------------------------------
if "yaml_path" not in st.session_state:
    st.session_state.yaml_path = "config.yaml"
if "use_yaml" not in st.session_state:
    st.session_state.use_yaml = USE_YAML_CONFIG_DEFAULT
if "cfg" not in st.session_state:
    st.session_state.cfg = load_config(
        yaml_path=st.session_state.yaml_path,
        use_yaml=st.session_state.use_yaml,
    )
if "pipe" not in st.session_state:
    st.session_state.pipe = RagPipeline(st.session_state.cfg)
if "qa" not in st.session_state:
    st.session_state.qa = None
# --- manifest_count (lightweight) ---
if "manifest_count" not in st.session_state:
    try:
        import sqlite3
        manifest_path = str(st.session_state.pipe.layout.manifest_db)
        if Path(manifest_path).exists():
            with sqlite3.connect(manifest_path) as conn:
                cur = conn.execute("SELECT COUNT(1) FROM manifest")
                row = cur.fetchone()
                st.session_state.manifest_count = (row[0] if row else 0) or 0
        else:
            st.session_state.manifest_count = 0
    except Exception:
        st.session_state.manifest_count = 0
if "show_llm_payload" not in st.session_state:
    st.session_state.show_llm_payload = True
if "prog_open" not in st.session_state:
    st.session_state.prog_open = False
# persisted progress state defaults
# Set initial phase based on whether indexing is needed
if st.session_state.manifest_count == 0:
    st.session_state.setdefault("index_phase", "starting...")
else:
    st.session_state.setdefault("index_phase", "idle")
st.session_state.setdefault("index_pct", 0)
st.session_state.setdefault("index_logs", [])
st.session_state.setdefault("index_summary", "")
st.session_state.setdefault("config_msg", "")

cfg = st.session_state.cfg
pipe = st.session_state.pipe

# Ensure DB is ready
ensure_db_ready()

# ---- (NEW) Start sparse compact daemon (once) ----
if not st.session_state.get("_sparse_compact_started"):
    try:
        from rag.vectorstores.sparse_compact_daemon import start_sparse_compact_daemon
        from rag.vectorstores.bm25_shards import BM25ShardSet  # ensure module import works
        sparse_cfg = getattr(cfg, "sparse", None)
        comp = getattr(sparse_cfg, "compaction", None) if sparse_cfg else None
        enabled = bool(getattr(comp, "enabled", True)) if comp is not None else True
        if enabled:
            shards_root = os.path.join(str(pipe.layout.index_dir), "sparse_shards")
            backend = str(getattr(sparse_cfg, "backend", "bm25s")).lower() if sparse_cfg else "bm25s"

            def _collect_items():
                ds = getattr(pipe.vindex, "_docstore", None)
                dct = getattr(ds, "_dict", None) if ds is not None else None
                if not isinstance(dct, dict):
                    return []
                out = []
                for cid, doc in dct.items():
                    md = getattr(doc, "metadata", {}) or {}
                    src = md.get("source") or md.get("file_path") or md.get("path") or ""
                    page = md.get("page") or md.get("page_number") or md.get("page_no") or ""
                    out.append((cid, f"{doc.page_content}\n[SRC:{src} P:{page}]"))
                return out

            start_sparse_compact_daemon(
                layout=pipe.layout,
                backend=backend,
                shards_root=shards_root,
                collect_items=_collect_items,
                interval_s=int(getattr(comp, "interval_s", 600)) if comp else 600,
                quiet_delay_s=int(getattr(comp, "quiet_delay_s", 300)) if comp else 300,
            )
            st.session_state._sparse_compact_started = True
    except Exception:
        pass

# Page config and title
st.set_page_config(page_title=cfg.app.page_title, layout="wide")
st.title(cfg.app.title)


# ------------------------------------------------------------------------------
# Admin: Users
# ------------------------------------------------------------------------------
def admin_users():
    st.subheader("Users")

    with Session(engine) as s:
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("Email (unique)")
            name = st.text_input("Name (optional)")
            pw = st.text_input("Password (optional)", type="password")

            if st.button("Create / Ensure", width="stretch"):
                if not email:
                    st.error("Email is required")
                else:
                    u = s.exec(select(User).where(User.email == email)).first()
                    if u:
                        if name:
                            u.name = name
                        if pw:
                            try:
                                u.password_hash = hash_password(pw)
                            except Exception:
                                u.password_hash = pw  # local dev fallback
                        s.add(u)
                        s.commit()
                        st.success(f"Updated user id={u.id} email={u.email}")
                    else:
                        try:
                            ph = hash_password(pw) if pw else None
                        except Exception:
                            ph = pw if pw else None
                        u = User(
                            email=email,
                            name=name or None,
                            password_hash=ph,
                            is_active=True,
                        )
                        s.add(u)
                        s.commit()
                        s.refresh(u)
                        st.success(f"Created user id={u.id} email={u.email}")

        with col2:
            users = s.exec(select(User).order_by(User.id.desc())).all()
            if not users:
                st.info("No users yet.")
            else:
                rows = []
                for u in users:
                    rows.append(
                        {
                            "id": u.id,
                            "email": u.email,
                            "name": u.name,
                            "is_active": u.is_active,
                            "created_at": getattr(u, "created_at", None),
                        }
                    )
                st.dataframe(rows, width="stretch")


# ------------------------------------------------------------------------------
# Admin: Data overview (users / conversations / messages)
# ------------------------------------------------------------------------------
def admin_data():
    st.subheader("Overview")

    with Session(engine) as s:
        users = s.exec(select(User).order_by(User.email.asc())).all()
        st.markdown(f"- **Users**: {len(users)}")

        # Only show these if the tables exist in your models
        try:
            convs = s.exec(select(Conversation)).all()
            st.markdown(f"- **Conversations**: {len(convs)}")
        except Exception:
            pass

        try:
            msgs = s.exec(select(Message)).all()
            st.markdown(f"- **Messages**: {len(msgs)}")
        except Exception:
            pass

        if users:
            rows = [{"id": u.id, "email": u.email, "name": u.name} for u in users]
            st.dataframe(rows, width="stretch")


# ------------------------------------------------------------------------------
# Admin: Login audit
# ------------------------------------------------------------------------------
def admin_logins():
    st.subheader("Login events")

    with Session(engine) as s:
        rows = s.exec(
            select(LoginEvent, User)
            .join(User, User.id == LoginEvent.user_id, isouter=True)
            .order_by(desc(LoginEvent.at))
            .limit(200)
        ).all()

    def fmt_ts(v: int | None):
        if v is None:
            return None
        v = int(v)
        # rough ms->s check
        if v > 10**12:
            v //= 1000
        return dt.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")

    data = []
    for le, u in rows:
        data.append(
            {
                "id": le.id,
                "when": fmt_ts(getattr(le, "at", None)),
                "user_id": le.user_id,
                "email": getattr(u, "email", None),
                "ip": getattr(le, "ip", None),
                "agent": getattr(le, "agent", None),
            }
        )

    if not data:
        st.info("No login events yet.")
        return

    st.dataframe(data, width="stretch")


# ------------------------------------------------------------------------------
# Sidebar: Progress, Settings, Info
# ------------------------------------------------------------------------------
with st.sidebar:
    # === TITLE ===
    st.markdown("### Control Panel")

    # === 1. PROGRESS TRACKING ===
    prog_card = st.container(border=True)
    with prog_card:
        # Current phase (placeholder) - always visible
        phase_ph = st.empty()
        phase_ph.markdown(f"**{st.session_state.index_phase}**")

        # Overall progress bar - always visible
        bar_ph = st.progress(st.session_state.index_pct)

        # Toggle button for detailed logs
        if st.button("Show Details" if not st.session_state.prog_open else "Hide Details",
                     key="prog_toggle", use_container_width=True):
            st.session_state.prog_open = not st.session_state.prog_open
            st.rerun()

        # Detailed logs - only visible when expanded
        log_ph = None
        if st.session_state.prog_open:
            st.caption("Detailed Logs")
            log_ph = st.empty()
            log_ph.text("\n".join(st.session_state.index_logs[-400:]))

    # === 2. INDEX MANAGEMENT ===
    index_card = st.container(border=True)
    with index_card:
        st.markdown("### Index Management")

        # Quick action buttons
        col1, col2 = st.columns(2)
        if col1.button("Refresh", help="Scan for changes and update index", use_container_width=True):
            # Clear previous logs before starting new operation
            st.session_state.index_logs = []
            st.session_state.index_phase = "starting..."
            st.session_state.index_pct = 0
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = ensure_index(st.session_state.pipe, force_clean=False, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.session_state.index_summary = f"Refresh complete. {st.session_state.manifest_count} files in manifest."

        if col2.button("Rebuild", help="Clean rebuild of entire index", use_container_width=True):
            # Clear previous logs before starting new operation
            st.session_state.index_logs = []
            st.session_state.index_phase = "starting..."
            st.session_state.index_pct = 0
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = ensure_index(st.session_state.pipe, force_clean=True, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.session_state.index_summary = f"Rebuild complete. {st.session_state.manifest_count} files indexed."

        # Status summary (appears inside Index Management card) - always visible
        status_ph = st.empty()
        if st.session_state.index_summary:
            status_ph.info(st.session_state.index_summary)

    # === 3. CONFIGURATION ===
    config_card = st.container(border=True)
    with config_card:
        st.markdown("### Configuration")

        # Config file settings
        with st.expander("Config File", expanded=False):
            st.text_input("config.yaml path", key="yaml_path", help="Path to configuration file")
            st.checkbox("Use YAML config", key="use_yaml", help="Use YAML file (else: ENV + defaults)")

            if st.button("Reload Config", use_container_width=True):
                st.session_state.cfg = load_config(
                    yaml_path=st.session_state.yaml_path,
                    use_yaml=st.session_state.use_yaml,
                )
                st.session_state.pipe = RagPipeline(st.session_state.cfg)
                # Clear QA and bootstrapped flag to force recreation
                st.session_state.qa = None
                st.session_state.index_bootstrapped = False
                st.session_state.config_msg = "Config reloaded. Rebuild to use new settings."

            # Config status placeholder (appears BELOW the button inside expander)
            config_status_ph = st.empty()
            if st.session_state.get("config_msg"):
                config_status_ph.success(st.session_state.config_msg)

        # Display options
        st.markdown("**Display Options**")
        st.checkbox("Show LLM prompt & context", key="show_llm_payload", help="Display full LLM request details")
        st.checkbox("Retrieval-only mode", key="force_ro", help="Skip LLM, only retrieve documents")

    # === 4. SYSTEM INFO ===
    info_card = st.container(border=True)
    with info_card:
        st.markdown("### System Info")
        st.caption(f"**Store:** `{st.session_state.pipe.layout.index_dir.parent}`")
        st.caption(f"**Index:** `{st.session_state.pipe.layout.index_dir}`")
        st.caption(f"**Manifest:** `{st.session_state.pipe.layout.manifest_db}`")
        st.caption(f"**Files:** {st.session_state.manifest_count}")

    # === 5. DANGER ZONE ===
    danger_card = st.container(border=True)
    with danger_card:
        st.markdown("### Danger Zone")

        # Danger zone status placeholder (appears inside Danger Zone card)
        danger_status_ph = st.empty()

        with st.expander("Factory Reset", expanded=False):
            st.warning(
                "**This will restore the app to factory state.**\n\n"
                "Deletes: all indexed data, cache, embeddings (`.rag_store/`)\n"
                "Keeps: source PDFs, config files\n\n"
                "**You must restart the app after factory reset.** Cannot be undone."
            )
            confirm = st.checkbox(
                "I understand and want to perform a factory reset.",
                key="confirm_full_clean",
            )

            # Error/success placeholder inside expander
            reset_msg_ph = st.empty()

            if st.button(
                "Factory Reset - Delete All Data",
                type="primary",
                width="stretch",
                key="btn_full_clean",
            ):
                if not confirm:
                    reset_msg_ph.error("Please tick the confirmation box above to confirm.")
                else:
                    # Clear all RAG data - requires app restart for clean state
                    with st.spinner("Deleting all indexed data..."):
                        clear_index(st.session_state.pipe)
                        # Also delete the entire .rag_store for full reset
                        try:
                            store_dir = Path(st.session_state.pipe.layout.index_dir).parent
                            if store_dir.exists() and store_dir.name in {".rag_store", "rag_store"}:
                                import shutil
                                shutil.rmtree(store_dir, ignore_errors=True)
                        except Exception as e:
                            reset_msg_ph.warning(f"Partial cleanup: {repr(e)}")

                    reset_msg_ph.success("Factory reset complete. **Please restart the app** (stop and run `./run_app.sh` again) to reinitialize with clean state.")

# ---- Ensure index is loaded/initialized (lazy) ----
if "index_bootstrapped" not in st.session_state:
    if st.session_state.manifest_count == 0:
        # No index exists -> do a full indexing with UI
        ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
        m = ensure_index(pipe, force_clean=False, ui=ui_map)
        st.session_state.manifest_count = len(m or [])
        # Update status box if present
        try:
            status_ph.info(st.session_state.index_summary)
        except Exception:
            pass
    else:
        # Index exists -> do NOT call pipe.bootstrap() yet.
        # Defer bootstrap until first Refresh/Rebuild or first user query.
        st.session_state.index_phase = "idle"
        st.session_state.index_pct = 0
        st.session_state.index_summary = f"Index ready. {st.session_state.manifest_count} files in manifest."
        try:
            phase_ph.markdown("**idle**")
            bar_ph.progress(0)
            status_ph.info(st.session_state.index_summary)
        except Exception:
            pass
    st.session_state.index_bootstrapped = True


# ------------------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------------------
tab_chat, tab_users, tab_data, tab_audit = st.tabs(
    ["Chat QA", "Admin - Users", "Admin - Data", "Admin - Logins"]
)

with tab_users:
    admin_users()

with tab_data:
    admin_data()

with tab_audit:
    admin_logins()

with tab_chat:
    # Build and memoize QA chain
    def build_qa_if_needed():
        if st.session_state.qa is not None:
            return st.session_state.qa
        qa_ = pipe.build_qa()
        st.session_state.qa = qa_
        return qa_

    qa = build_qa_if_needed()

    llm_disabled = bool(st.session_state.get("force_ro")) or (
        isinstance(qa, dict) and qa.get("llm") == "disabled"
    )
    if llm_disabled:
        st.info("LLM disabled (config: `llm.enabled=false`). Retrieval-only mode.")

    query = st.text_input(cfg.app.ui.input_label, key="user_query")
    if query:
        with st.status("Retrieving...", expanded=True) as status:
            try:
                # Retrieve first for instant feedback
                retriever = pipe.serve()
                try:
                    docs = retriever.invoke(query)  # new interface
                except TypeError:
                    docs = retriever.get_relevant_documents(query)  # legacy interface
                docs = docs or []
                status.write(f"Retrieved {len(docs)} chunk(s).")

                if llm_disabled:
                    status.update(
                        label="LLM disabled - showing retrieval only.", state="complete"
                    )
                    st.subheader("Top Chunks")
                    if not docs:
                        st.write("_No matches_")
                    else:
                        for i, d in enumerate(docs[:5], 1):
                            src = d.metadata.get("source")
                            page = d.metadata.get("page_number", d.metadata.get("page"))
                            st.markdown(f"**{i}.** `{src}` (page {page})")
                            text = d.page_content or ""
                            st.write(text[:600] + ("..." if len(text) > 600 else ""))
                            st.markdown("---")
                    raise SystemExit  # normal early return

                # Call LLM
                status.update(label="Calling LLM...", state="running")
                spy = PromptSpy()
                try:
                    res = qa.invoke(
                        {"query": query}, config={"callbacks": [spy]}
                    )  # new interface
                except TypeError:
                    res = qa({"query": query}, callbacks=[spy])  # legacy interface

                # Normalize variants
                if isinstance(res, dict):
                    answer_text = (
                        res.get("result")
                        or res.get("answer")
                        or res.get("output_text")
                        or ""
                    )
                    src_docs = res.get("source_documents") or docs
                elif isinstance(res, str):
                    answer_text = res
                    src_docs = docs
                else:
                    answer_text = str(res)
                    src_docs = docs

                st.subheader("Answer")
                st.write(answer_text if answer_text.strip() else "_(empty answer)_")

                if st.session_state.show_llm_payload:
                    payload = (
                        res
                        if isinstance(res, dict)
                        else {
                            "result": answer_text,
                            "source_documents": src_docs,
                        }
                    )
                    render_prompt_spy(spy, payload)

                if src_docs:
                    st.subheader("Sources")
                    for i, d in enumerate(src_docs[:5], 1):
                        src = d.metadata.get("source")
                        page = d.metadata.get("page_number", d.metadata.get("page"))
                        st.markdown(f"**{i}.** `{src}` (page {page})")

                status.update(label="Done", state="complete")

            except SystemExit:
                pass
            except Exception as e:  # pragma: no cover
                status.update(label="Error while answering", state="error")
                st.error(f"{type(e).__name__}: {e}")
                st.exception(e)
