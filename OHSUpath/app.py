# app.py

from __future__ import annotations
import streamlit as st
import shutil
from pathlib import Path
from config import load_config
from rag.pipeline import RagPipeline
import multiprocessing as _mp
try:
    _mp.set_start_method("spawn", force=True)
except (RuntimeError, ValueError):
    pass

try:
    from langchain_core.callbacks import BaseCallbackHandler
except Exception:
    from langchain.callbacks.base import BaseCallbackHandler

# ------------------------------------------------------------
# CONFIGURATION MODE SWITCH
# True  = Use YAML + env variables + defaults in config.py
# False = Use ONLY env variables + defaults in config.py
# ------------------------------------------------------------
USE_YAML_CONFIG_DEFAULT: bool = False   # True = use YAML, False = skip YAML


class PromptSpy(BaseCallbackHandler):
    """Collects prompts/messages/params observed via LangChain callbacks."""

    def __init__(self):
        self.text_prompts: list[str] = []
        self.chat_prompts: list[list[object]] = []
        self.params: dict = {}

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Capture text prompts and invocation params."""
        if prompts:
            self.text_prompts.extend(prompts)
        self.params = kwargs.get("invocation_params", self.params)

    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Capture chat messages and invocation params."""
        if messages:
            self.chat_prompts.extend(messages)
        self.params = kwargs.get("invocation_params", self.params)


def _render_prompt_spy(spy: PromptSpy, res: dict):
    """Render an expandable panel with prompts, params, and top context chunks."""
    with st.expander("What we sent to the LLM (prompt + context)", expanded=False):
        if spy.text_prompts:
            for i, p in enumerate(spy.text_prompts, 1):
                st.markdown(f"**Prompt {i}**")
                st.code(p)
        if spy.chat_prompts:
            for ri, run_msgs in enumerate(spy.chat_prompts, 1):
                st.markdown(f"**Chat Run {ri}**")
                for mi, m in enumerate(run_msgs, 1):
                    role = getattr(m, "type", None) or getattr(m, "role", None) or m.__class__.__name__
                    content = getattr(m, "content", "")
                    st.markdown(f"- **{mi}. {role}**")
                    st.code(content)
        if not spy.text_prompts and not spy.chat_prompts:
            st.info("No prompt was intercepted from callbacks (expected if your chain/provider doesn't propagate).")
        if spy.params:
            st.markdown("**LLM Params**")
            st.json(spy.params)
        docs = res.get("source_documents", []) or []
        if docs:
            st.markdown("**Context Chunks (top)**")
            for i, d in enumerate(docs[:5], 1):
                src = d.metadata.get("source")
                page = d.metadata.get("page_number", d.metadata.get("page"))
                st.markdown(f"**{i}.** `{src}`  (page {page})")
                st.write(d.page_content[:800] + ("..." if len(d.page_content) > 800 else ""))
                st.caption(str(d.metadata))
                st.markdown("---")


# ---- index helpers ----
def _clear_index(pipe: RagPipeline):
    """Remove the index directory and manifest DB if present (best-effort)."""
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


def _ensure_index(
    pipe: RagPipeline,
    *,
    force_clean: bool = False,
    ui: dict | None = None,
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
    bar_ph   = ui.get("bar")
    log_ph   = ui.get("log")

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
        "diff":     "scanning...",
        "load":     "indexing...",
        "split":    "splitting...",
        "embed":    "embedding...",
        "commit":   "committing...",
    }
    weights = {"discover": 0.05, "diff": 0.05, "load": 0.20, "split": 0.20, "embed": 0.40, "commit": 0.10}
    seen: set[str] = set()

    # If rerun occurs within one session, we recompute pct from seen for simplicity
    def _pct() -> int:
        return int(sum(weights[p] for p in seen if p in weights) * 100)

    def _render_logs():
        if log_ph:
            # Render last 400 lines to keep the DOM light
            log_ph.text("\n".join(st.session_state.index_logs[-400:]))

    def _push(line: str):
        st.session_state.index_logs.append(line)
        _render_logs()

    def _bump(base: str):
        if base in weights and base not in seen:
            seen.add(base)
            pct = min(_pct(), 100)
            st.session_state.index_pct = pct
            bar_handle.progress(pct)

    if force_clean:
        _push(f"[info] Rebuilding index under: {pipe.layout.index_dir.parent}")

    try:
        prev = pipe.bootstrap()
    except RuntimeError as e:
        msg = str(e)
        if "Index meta mismatch" in msg:
            _push("[warn] Detected index meta mismatch. Cleaning index + manifest, then rebuilding...")
            _clear_index(pipe)
            prev = pipe.bootstrap()
        else:
            st.session_state.index_phase = "error"
            if phase_ph:
                phase_ph.markdown("**error**")
            st.session_state.index_pct = 100
            bar_handle.progress(100)
            _push(f"[error] {repr(e)}")
            raise

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
                _push(f"- {base}... {kw}")
            elif event.endswith("_done"):
                _push(f"[OK] {base} done. {kw}")
                _bump(base)
            elif event in ("discover", "diff"):
                _push(f"[OK] {base}. {kw}")
                _bump(base)
            elif event == "refresh_error":
                _push(f"[ERROR] {kw.get('error')}")
            else:
                _push(f"- {event}: {kw}")

        curr = pipe.refresh(prev, progress=on_progress)
    except Exception as e:
        st.session_state.index_phase = "error"
        if phase_ph:
            phase_ph.markdown("**error**")
        st.session_state.index_pct = 100
        bar_handle.progress(100)
        _push(f"[error] {repr(e)}")
        raise
    else:
        st.session_state.index_phase = "complete"
        st.session_state.index_pct = 100
        bar_handle.progress(100)
        if phase_ph:
            phase_ph.markdown("**complete**")
        st.session_state.index_summary = f"Indexing complete ({len(curr)} files)."
        _push(f"[ok] {st.session_state.index_summary}")
        return curr
    
def _clear_project_artifacts(pipe: RagPipeline):
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
    _clear_index(pipe)

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
        else:
            pass
    except Exception:
        pass

    # 3) .pytest_cache
    try:
        shutil.rmtree(root / ".pytest_cache", ignore_errors=True)
    except Exception:
        pass

    # 4) __pycache__
    try:
        for p in root.rglob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass

    # 5) *.pyc
    try:
        for p in root.rglob("*.pyc"):
            try:
                p.unlink()
            except Exception:
                pass
    except Exception:
        pass



# ---- page title ----
def _page_title(cfg):
    """Apply page title and header based on config."""
    st.set_page_config(page_title=cfg.app.page_title)
    st.title(cfg.app.title)


# ---- Session init ----
if "yaml_path" not in st.session_state:
    st.session_state.yaml_path = "config.yaml"
if "use_yaml" not in st.session_state:
    st.session_state.use_yaml = USE_YAML_CONFIG_DEFAULT
if "cfg" not in st.session_state:
    st.session_state.cfg = load_config(yaml_path=st.session_state.yaml_path, use_yaml=st.session_state.use_yaml)
if "pipe" not in st.session_state:
    st.session_state.pipe = RagPipeline(st.session_state.cfg)
if "qa" not in st.session_state:
    st.session_state.qa = None
if "manifest_count" not in st.session_state:
    st.session_state.manifest_count = 0
if "show_llm_payload" not in st.session_state:
    st.session_state.show_llm_payload = True
# progress card open/closed
if "prog_open" not in st.session_state:
    st.session_state.prog_open = False
# persisted progress state defaults
st.session_state.setdefault("index_phase", "idle")
st.session_state.setdefault("index_pct", 0)
st.session_state.setdefault("index_logs", [])
st.session_state.setdefault("index_summary", "")

cfg = st.session_state.cfg
pipe = st.session_state.pipe
_page_title(cfg)

# ---- SIDEBAR modules ----
with st.sidebar:
    # === Custom Progress Card (collapsible) ===
    prog_card = st.container(border=True)
    with prog_card:
        # Header button toggles card expansion; summary stays inside the same card
        arrow = "v" if st.session_state.prog_open else ">"
        label = f"{arrow} Progress"
        if st.button(label, key="prog_toggle", use_container_width=True):
            st.session_state.prog_open = not st.session_state.prog_open

        # Row 2: current phase (placeholder) - always visible
        phase_ph = st.empty()
        phase_ph.markdown(f"**{st.session_state.index_phase}**")

        # Row 3: overall progress bar - always visible
        bar_ph = st.progress(st.session_state.index_pct)

        # Details (logs) - only visible when expanded
        log_ph = None
        if st.session_state.prog_open:
            st.caption("Details")
            log_ph = st.empty()
            # show last logs immediately
            log_ph.text("\n".join(st.session_state.index_logs[-400:]))

    # === Settings module ===
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
                yaml_path=st.session_state.yaml_path,
                use_yaml=st.session_state.use_yaml,
            )
            st.session_state.pipe = RagPipeline(st.session_state.cfg)
            st.success("Config reloaded. You may reindex if you changed embedding model/dim/metric.")

        if colB.button("Reindex (clean)"):
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = _ensure_index(st.session_state.pipe, force_clean=True, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.success(f"Reindex done. {st.session_state.manifest_count} files indexed.")

        if st.button("Refresh (scan changes)"):
            ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
            c = _ensure_index(st.session_state.pipe, force_clean=False, ui=ui_map)
            st.session_state.manifest_count = len(c or [])
            st.success(f"Refresh done. {st.session_state.manifest_count} files in manifest.")

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
                key="confirm_full_clean"
            )

            if st.button(
                "Factory Reset — delete & rebuild",
                type="primary",
                use_container_width=True,
                key="btn_full_clean"
            ):
                if not confirm:
                    st.error("Please tick the confirmation box above to confirm.")
                else:
                    with st.spinner("Processing…"):
                        ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
                        _clear_project_artifacts(st.session_state.pipe)
                        c = _ensure_index(st.session_state.pipe, force_clean=False, ui=ui_map)
                        st.session_state.manifest_count = len(c or [])
                    st.success(f"Factory reset complete. {st.session_state.manifest_count} files indexed.")

    # === Info module ===
    info_card = st.container(border=True)
    with info_card:
        st.markdown("**Info**")
        store_dir = st.session_state.pipe.layout.index_dir.parent
        st.caption(f"Store dir: `{store_dir}`")
        st.caption(f"Index dir: `{st.session_state.pipe.layout.index_dir}`")
        st.caption(f"Manifest: `{st.session_state.pipe.layout.manifest_db}`")

# ---- first-time ensure index (render into the same progress card placeholders) ----
if st.session_state.manifest_count == 0:
    ui_map = {"phase": phase_ph, "bar": bar_ph, "log": log_ph}
    m = _ensure_index(pipe, force_clean=False, ui=ui_map)
    st.session_state.manifest_count = len(m or [])

# ---- build QA ----
def _build_qa_if_needed():
    """Lazy-initialize the QA chain and memoize it in session_state."""
    if st.session_state.qa is not None:
        return st.session_state.qa
    qa = pipe.build_qa()
    st.session_state.qa = qa
    return qa

qa = _build_qa_if_needed()
# Determine whether LLM is disabled: explicit toggle or config-driven
llm_disabled = bool(st.session_state.get("force_ro")) or (isinstance(qa, dict) and qa.get("llm") == "disabled")

if llm_disabled:
    st.info("LLM disabled (config: `llm.enabled=false`). Running in retrieval-only mode.")

# ---- Main (kept clean) ----
query = st.text_input(cfg.app.ui.input_label, key="user_query")
if query:
    with st.status("Retrieving...", expanded=True) as status:
        try:
            # Retrieve first so the user sees immediate progress (LLM may be slow)
            retriever = pipe.serve()
            try:
                docs = retriever.invoke(query)  # LangChain new interface
            except TypeError:
                docs = retriever.get_relevant_documents(query)  # Legacy interface
            docs = docs or []
            status.write(f"Retrieved {len(docs)} chunk(s).")

            # Short-circuit if retrieval-only mode is active or LLM is disabled
            if llm_disabled:
                status.update(label="LLM disabled - showing retrieval only.", state="complete")
                st.subheader("Top Chunks")
                if not docs:
                    st.write("_No matches_")
                else:
                    for i, d in enumerate(docs[:5], 1):
                        src = d.metadata.get("source")
                        page = d.metadata.get("page_number", d.metadata.get("page"))
                        st.markdown(f"**{i}.** `{src}` (page {page})")
                        st.write(d.page_content[:600] + ("..." if len(d.page_content) > 600 else ""))
                        st.markdown("---")
                raise SystemExit  # End this render (not an error)

            # Update status before calling the LLM
            status.update(label="Calling LLM...", state="running")

            spy = PromptSpy()
            try:
                res = qa.invoke({"query": query}, config={"callbacks": [spy]})  # New interface
            except TypeError:
                res = qa({"query": query}, callbacks=[spy])                    # Legacy interface

            # Normalize result variants: dict/str/other; also normalize sources
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
                payload = res if isinstance(res, dict) else {"result": answer_text, "source_documents": src_docs}
                _render_prompt_spy(spy, payload)

            if src_docs:
                st.subheader("Sources")
                for i, d in enumerate(src_docs[:5], 1):
                    src = d.metadata.get("source")
                    page = d.metadata.get("page_number", d.metadata.get("page"))
                    st.markdown(f"**{i}.** `{src}` (page {page})")

            status.update(label="Done", state="complete")

        except SystemExit:
            pass  # Early return for retrieval-only mode
        except Exception as e:
            status.update(label="Error while answering", state="error")
            st.error(f"{type(e).__name__}: {e}")
            st.exception(e)
