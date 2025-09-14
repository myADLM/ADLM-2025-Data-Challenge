# app.py

from __future__ import annotations
import streamlit as st
import shutil
from pathlib import Path
import datetime as dt
from sqlalchemy import desc
from sqlmodel import Session, select, SQLModel
from config import load_config
from rag.pipeline import RagPipeline
import sys, pathlib

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

    def on_llm_start(self, serialized, prompts, **kwargs):
        if prompts:
            self.text_prompts.extend(prompts)
        self.params = kwargs.get("invocation_params", self.params)

    def on_chat_model_start(self, serialized, messages, **kwargs):
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

    # bootstrap
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
            - '{phase}_done'  -> log + bump progress
            - 'discover'/'diff' -> treat as completed phases
            - 'refresh_error' -> error log
            """
            base = event.replace("_start", "").replace("_done", "")
            if event.endswith("_start"):
                st.session_state.index_phase = label_map.get(base, base)
                if phase_ph:
                    phase_ph.markdown(f"**{st.session_state.index_phase}**")
                push(f"- {base}... {kw}")
            elif event.endswith("_done"):
                push(f"[OK] {base} done. {kw}")
                bump(base)
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
if "manifest_count" not in st.session_state:
    st.session_state.manifest_count = 0
if "show_llm_payload" not in st.session_state:
    st.session_state.show_llm_payload = True
if "prog_open" not in st.session_state:
    st.session_state.prog_open = False

# Sidebar progress state
st.session_state.setdefault("index_phase", "idle")
st.session_state.setdefault("index_pct", 0)
st.session_state.setdefault("index_logs", [])
st.session_state.setdefault("index_summary", "")

cfg = st.session_state.cfg
pipe = st.session_state.pipe

# Ensure DB is ready
ensure_db_ready()

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
    # Progress card
    prog_card = st.container(border=True)
    with prog_card:
        arrow = "v" if st.session_state.prog_open else ">"
        label = f"{arrow} Progress"
        if st.button(label, key="prog_toggle", width="stretch"):
            st.session_state.prog_open = not st.session_state.prog_open

        phase_ph = st.empty()
        phase_ph.markdown(f"**{st.session_state.index_phase}**")

        bar_ph = st.progress(st.session_state.index_pct)

        log_ph = None
        if st.session_state.prog_open:
            st.caption("Details")
            log_ph = st.empty()
            log_ph.text("\n".join(st.session_state.index_logs[-400:]))

    # Settings card
    set_card = st.container(border=True)
    with set_card:
        st.markdown("**Settings**")
        if st.session_state.index_summary:
            st.info(st.session_state.index_summary)
        st.text_input("config.yaml path", key="yaml_path")
        st.checkbox("Use YAML (else: defaults + ENV only)", key="use_yaml")
        st.checkbox("Show LLM request (prompt + context)", key="show_llm_payload")
        st.checkbox("Force retrieval-only (skip LLM)", key="force_ro")

        colA, colB = st.columns(2)
        if colA.button("Reload config"):
            st.session_state.cfg = load_config(
                yaml_path=st.session_state.yaml_path, use_yaml=st.session_state.use_yaml
            )
            st.session_state.pipe = RagPipeline(st.session_state.cfg)
            st.success(
                "Config reloaded. If you changed embedding dim/metric, consider Reindex."
            )

        if colB.button("Reindex (clean)"):
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = ensure_index(st.session_state.pipe, force_clean=True, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.success(
                f"Reindex done. {st.session_state.manifest_count} files indexed."
            )

        if st.button("Refresh (scan changes)"):
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = ensure_index(st.session_state.pipe, force_clean=False, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.success(
                f"Refresh done. {st.session_state.manifest_count} files in manifest."
            )

        with st.container(border=True):
            st.markdown("### Factory Reset (restore to default state)")
            st.warning(
                "This will restore the app to its **factory state**.\n\n"
                "**It will permanently delete:** all trained data on this device.\n\n"
                "**It will NOT delete or change:** source PDFs under `data/` or `minidata/`,`config file`.\n\n"
                "Rebuilding the index may take time. **This action cannot be undone.**"
            )
            confirm = st.checkbox(
                "I understand and want to perform a factory reset.",
                key="confirm_full_clean",
            )

            if st.button(
                "Factory Reset - delete and rebuild",
                type="primary",
                width="stretch",
                key="btn_full_clean",
            ):
                if not confirm:
                    st.error("Please tick the confirmation box above.")
                else:
                    with st.spinner("Processing..."):
                        ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
                        clear_project_artifacts(st.session_state.pipe)
                        c = ensure_index(
                            st.session_state.pipe, force_clean=False, ui=ui_map
                        )
                        st.session_state.manifest_count = len(c or [])
                    st.success(
                        f"Factory reset complete. {st.session_state.manifest_count} files indexed."
                    )

    # Info card
    info_card = st.container(border=True)
    with info_card:
        st.markdown("**Info**")
        store_dir = st.session_state.pipe.layout.index_dir.parent
        st.caption(f"Store dir: `{store_dir}`")
        st.caption(f"Index dir: `{st.session_state.pipe.layout.index_dir}`")
        st.caption(f"Manifest: `{st.session_state.pipe.layout.manifest_db}`")

# First-time index refresh
if st.session_state.manifest_count == 0:
    ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
    m = ensure_index(pipe, force_clean=False, ui=ui_map)
    st.session_state.manifest_count = len(m or [])


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
