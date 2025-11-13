import os
import platform
import subprocess
from typing import Dict, List, Iterable, Tuple, Optional
import streamlit as st

import backend  # your backend.py (below)

# ---------------- Page & Theme ----------------
st.set_page_config(page_title="Clinical RAG — Notebook View", layout="wide")

if "dark" not in st.session_state:
    st.session_state.dark = True

def toggle_theme():
    st.session_state.dark = not st.session_state.dark

st.markdown(
    f"""
    <style>
      :root {{
        --sidebar-w: 320px;
        --radius: 16px;
        --border: {"#27272a" if st.session_state.dark else "#e5e7eb"};
        --card: {"#0b0b0c" if st.session_state.dark else "#ffffff"};
        --soft: {"rgba(24,24,27,0.35)" if st.session_state.dark else "rgba(250,250,250,0.76)"};
        --text: {"#fafafa" if st.session_state.dark else "#0b0b0c"};
        --muted: {"#a1a1aa" if st.session_state.dark else "#6b7280"};
        --chip-bg: {"#111827" if st.session_state.dark else "#ffffff"};
        --chip-br: {"#374151" if st.session_state.dark else "#e5e7eb"};
        --bg: {"#0a0a0a" if st.session_state.dark else "#ffffff"};
      }}
      html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg);
        color: var(--text);
      }}
      [data-testid="stSidebar"] {{
        width: var(--sidebar-w) !important;
        min-width: var(--sidebar-w) !important;
        max-width: var(--sidebar-w) !important;
      }}
      [data-testid="stSidebar"] > div:first-child {{ width: var(--sidebar-w) !important; }}
      [data-testid="stSidebar"][aria-expanded="true"] ~ header[data-testid="stHeader"] {{
        margin-left: var(--sidebar-w);
        width: calc(100% - var(--sidebar-w));
      }}
      [data-testid="stSidebar"][aria-expanded="true"] ~ div[data-testid="stAppViewContainer"] {{
        margin-left: var(--sidebar-w);
      }}
      .card {{
        border: 1px solid var(--border);
        background: var(--card);
        border-radius: 16px;
        padding: 16px;
      }}
      .soft {{
        border: 1px solid var(--border);
        background: var(--soft);
        backdrop-filter: blur(6px);
        border-radius: 16px;
        padding: 16px;
      }}
      .chip {{
        display: inline-flex; gap: 6px; align-items: center;
        border: 1px solid var(--chip-br);
        background: var(--chip-bg);
        border-radius: 999px; padding: 4px 10px; font-size: 11px;
        color: var(--text);
        text-decoration: none;
      }}
      .tiny {{ color: var(--muted); font-size: 11px; }}
      .sep {{ height: 1px; background: var(--border); width: 100%; margin: 8px 0; }}
      div[data-testid="stExpander"] details summary p {{ display: inline; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_relevant_documents" not in st.session_state:
    st.session_state.last_relevant_documents = []
if "running" not in st.session_state:
    st.session_state.running = False

# ---------------- Utilities ----------------
def open_local_file(path: str):
    """Open a local file if running locally."""
    if not path or not os.path.exists(path):
        st.warning("File not found.")
        return
    try:
        sys = platform.system()
        if sys == "Windows":
            os.startfile(path)  # type: ignore
        elif sys == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        st.warning(f"Could not open file: {e}")

def render_relevant_documents_inline(relevant_documents: List[Dict]):
    if not relevant_documents:
        return
    st.markdown("<div class='soft'><b>Relevant Documents</b>", unsafe_allow_html=True)
    for c in relevant_documents:
        title = c.get("title") or c.get("path") or c.get("url") or "source"
        url, path, score = c.get("url"), c.get("path"), c.get("score")
        meta = [str(c[k]) for k in ("section", "kind") if c.get(k)]
        if isinstance(score, (int, float)):
            meta.append(f"score {score:.4f}")
        meta_txt = " · ".join(meta)
        label = f"{title}" + (f" &nbsp;<span class='tiny'>{meta_txt}</span>" if meta_txt else "")
        if url:
            st.markdown(f"<a class='chip' href='{url}' target='_blank'>{label}</a>", unsafe_allow_html=True)
        elif path and os.path.exists(path):
            cols = st.columns([1, 3])
            with cols[0]:
                st.button("Open", key=f"open_{path}", on_click=open_local_file, args=(path,))
            with cols[1]:
                st.markdown(f"<span class='chip'>{label}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='chip'>{label}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Layout ----------------
with st.sidebar:
    st.markdown("### Relevant files")
    st.caption("From the last answer")
    cites = st.session_state.last_relevant_documents or []
    if not cites:
        st.info("No relevant documents yet.")
    else:
        for c in cites:
            title = c.get("title") or c.get("path") or c.get("url") or "source"
            meta = " · ".join(str(c[k]) for k in ("section", "kind") if c.get(k))
            url, path = c.get("url"), c.get("path")
            if url:
                st.markdown(f"- [{title}]({url})  \n  <span class='tiny'>{meta}</span>", unsafe_allow_html=True)
            elif path and os.path.exists(path):
                cols = st.columns([1, 5])
                with cols[0]:
                    st.button("Open", key=f"open_sidebar_{path}", on_click=open_local_file, args=(path,))
                with cols[1]:
                    st.markdown(f"**{title}**  \n<span class='tiny'>{meta}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"- **{title}**  \n  <span class='tiny'>{meta}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("🌗 Toggle theme", use_container_width=True, on_click=toggle_theme)

st.markdown("#### Clinical RAG — Notebook view")

# ---------------- Chat Logic ----------------
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        st.markdown(msg["content"])
        if role == "assistant" and msg.get("relevant_documents"):
            render_relevant_documents_inline(msg["relevant_documents"])

prompt = st.chat_input("Ask a clinical question…")
if prompt and not st.session_state.running:
    st.session_state.running = True
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        chunks_iter, relevant_docs = backend.query_stream(prompt)
        content = ""
        for chunk in chunks_iter:
            content += str(chunk)
            placeholder.markdown(content)
        render_relevant_documents_inline(relevant_docs)

    st.session_state.last_relevant_documents = relevant_docs
    st.session_state.messages.append({"role": "assistant", "content": content, "relevant_documents": relevant_docs})
    st.session_state.running = False
    st.rerun()
