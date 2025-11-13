import os
import csv
from datetime import datetime
import streamlit as st

# LangChain / Chroma
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function

st.set_page_config(layout="wide")

# --- Sidebar width without bleeding into the main content ---
st.markdown(
    """
    <style>
      /* Change this value once; everything else follows */
      :root { --my-sidebar-width: 380px; }

      /* Make the sidebar that exact width */
      [data-testid="stSidebar"] {
        width: var(--my-sidebar-width) !important;
        min-width: var(--my-sidebar-width) !important;
        max-width: var(--my-sidebar-width) !important;
      }
      [data-testid="stSidebar"] > div:first-child {
        width: var(--my-sidebar-width) !important;
      }

      /* When the sidebar is expanded, offset the app and header by the same width */
      [data-testid="stSidebar"][aria-expanded="true"] ~ div[data-testid="stAppViewContainer"] {
        margin-left: var(--my-sidebar-width);
      }
      [data-testid="stSidebar"][aria-expanded="true"] ~ header[data-testid="stHeader"] {
        margin-left: var(--my-sidebar-width);
        width: calc(100% - var(--my-sidebar-width));
      }

      /* When collapsed (or in narrow layouts), remove the offset */
      [data-testid="stSidebar"][aria-expanded="false"] ~ div[data-testid="stAppViewContainer"],
      [data-testid="stSidebar"][aria-expanded="false"] ~ header[data-testid="stHeader"] {
        margin-left: 0;
        width: 100%;
      }

      /* Mobile: let the sidebar overlay and keep main full width */
      @media (max-width: 992px) {
        [data-testid="stSidebar"] {
          width: 85vw !important;
          min-width: 85vw !important;
          max-width: 85vw !important;
        }
        [data-testid="stSidebar"][aria-expanded="true"] ~ div[data-testid="stAppViewContainer"],
        [data-testid="stSidebar"][aria-expanded="true"] ~ header[data-testid="stHeader"] {
          margin-left: 0;
          width: 100%;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Helpers: Chroma discovery
# =========================

def _is_chroma_persist_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    sentinels = ["chroma.sqlite3", "chroma.sqlite", "index", "index.sqlite"]
    return any(os.path.exists(os.path.join(path, s)) for s in sentinels)

def list_persist_dirs(base_dir: str = "chroma"):
    candidates = []
    if os.path.isdir(base_dir) and _is_chroma_persist_dir(base_dir):
        candidates.append(os.path.normpath(base_dir))
    if os.path.isdir(base_dir):
        for name in os.listdir(base_dir):
            p = os.path.join(base_dir, name)
            if _is_chroma_persist_dir(p):
                candidates.append(os.path.normpath(p))
    return sorted(set(candidates))

def list_collections_in_persist_dir(persist_dir: str):
    try:
        import chromadb  # ensures chromadb is installed
        client = chromadb.PersistentClient(path=persist_dir)
        colls = client.list_collections()
        names = []
        for c in colls:
            name = getattr(c, "name", None) or getattr(c, "id", None) or (c.get("name") if isinstance(c, dict) else None)
            if name:
                names.append(name)
        return sorted(set(names))
    except Exception:
        return None

def default_collection_for_dir(persist_dir: str, prefix: str = "ADLM_Embeddings_") -> str:
    base = os.path.basename(os.path.normpath(persist_dir))
    safe_model = base.replace(":", "_")
    return f"{prefix}{safe_model}"


# =========================
# UI & Session State Setup
# =========================

st.set_page_config(page_title="RAG Query UI", layout="wide")

if "history" not in st.session_state:
    # List of dicts:
    #   {"ts", "query", "response", "sources", "chroma_path", "collection_name", "llm_model", "embedding_model"}
    st.session_state.history = []

if "selected_history_idx" not in st.session_state:
    st.session_state.selected_history_idx = None

if "last_run" not in st.session_state:
    st.session_state.last_run = None  # store the latest run dict for display after execution


# =========================
# Sidebar: Settings + History
# =========================

st.sidebar.title("Vector Database Options")

base_dir = st.sidebar.text_input("Base Chroma folder", value="chroma")
refresh = st.sidebar.button("🔄 Refresh")

persist_dirs = list_persist_dirs(base_dir)
choices = persist_dirs + ["Other…"] if persist_dirs else ["Other…"]
chroma_path_choice = st.sidebar.selectbox("Chroma DB path", options=choices, index=0)

if chroma_path_choice == "Other…":
    chroma_path = st.sidebar.text_input("Custom Chroma path")
else:
    chroma_path = chroma_path_choice

collection_options = list_collections_in_persist_dir(chroma_path) if chroma_path else None
default_coll = default_collection_for_dir(chroma_path) if chroma_path else "ADLM_Embeddings_default"
collection_name = st.sidebar.selectbox("Collection name", options=collection_options if collection_options else [default_coll], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("History")

# Clear history button
if st.sidebar.button("🧹 Clear history"):
    st.session_state.history = []
    st.session_state.selected_history_idx = None

# Show at most the last 25 entries; newest first
for idx, item in enumerate(reversed(st.session_state.history[-25:])):
    # Compute the actual index in history list
    real_idx = len(st.session_state.history) - 1 - idx
    ts_short = datetime.fromisoformat(item["ts"]).strftime("%H:%M:%S")
    label = f"{ts_short} · {item['query'][:60]}{'…' if len(item['query']) > 60 else ''}"
    if st.sidebar.button(label, key=f"hist_btn_{real_idx}"):
        st.session_state.selected_history_idx = real_idx

# If history selection clicked, show that result in main without re-running
selected_snapshot = None
if st.session_state.selected_history_idx is not None:
    selected_snapshot = st.session_state.history[st.session_state.selected_history_idx]


# =========================
# Main Panel
# =========================

st.title("ADLM Challenge QC RAG Query Interface")

col1, col2, col3 = st.columns([3, 1.5, 1.5])

query = st.text_input("Enter your question:")

llm_model = st.text_input("Local LLM", value="gpt-oss:20b")

log_csv = st.text_input("Results CSV (optional):", value="QC-Logs/QC_results.csv")

run = st.button("Run Query")

PROMPT_TEMPLATE = """
Answer the question using the context below if relevant. If the context doesn’t contain the answer, respond 'Context not found.'

{context}

---

Answer the question based on the above context: {question}
"""

def build_sources_table(results):
    """Convert (Document, score) pairs into a list of rows ready for display."""
    table = []
    for rank, (doc, score) in enumerate(results, start=1):
        meta = dict(doc.metadata or {})
        # Try to derive a reasonable ID/title/link
        doc_id = meta.get("id") or meta.get("source") or meta.get("path") or f"doc_{rank}"
        link = meta.get("url") or meta.get("source") or meta.get("path")
        # Title preference: explicit title, basename of path/source, fallback to doc_id
        title = (
            meta.get("title")
            or (os.path.basename(link) if link and isinstance(link, str) else None)
            or str(doc_id)
        )
        snippet = (doc.page_content[:500] + "…") if doc.page_content and len(doc.page_content) > 500 else doc.page_content
        row = {
            "rank": rank,
            "doc_id": str(doc_id),
            "title": str(title),
            "score": float(score) if score is not None else None,
            "link": link if isinstance(link, str) else None,
            "snippet": snippet or "",
            "metadata": meta,
        }
        table.append(row)
    return table

def render_sources_nice(table_rows):
    """Pretty render of the sources with expanders, links, scores, snippets."""
    st.markdown("### Sources")
    if not table_rows:
        st.info("No sources.")
        return

    # Summary table at a glance
    try:
        import pandas as pd
        summary = pd.DataFrame(
            [
                {
                    "Rank": r["rank"],
                    "Title": r["title"],
                    "Doc ID": r["doc_id"],
                    "Score": r["score"],
                    "Link": r["link"],
                }
                for r in table_rows
            ]
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
    except Exception:
        pass

    # Detailed expandable cards
    for r in table_rows:
        score_str = f"{r['score']:.4f}" if isinstance(r["score"], (int, float)) else "n/a"
        header = f"{r['rank']}. {r['title']}  —  score: {score_str}"
        with st.expander(header, expanded=False):
            if r["link"]:
                st.markdown(f"**Source:** [{r['link']}]({r['link']})")
            st.markdown("**Snippet:**")
            st.code(r["snippet"] or "", language="markdown")
            with st.popover("Show full metadata"):
                st.json(r["metadata"])

def log_to_csv(csv_path, query, embedding_model, chroma_path, collection_name, llm_model, llm_output, sources_ids):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True) if os.path.dirname(csv_path) else None
    row = {
        "query": query,
        "embedding_model": embedding_model,
        "chroma_path": chroma_path,
        "collection_name": collection_name,
        "llm_model": llm_model,
        "llm_output": llm_output,
        "sources": ";".join([str(s) for s in sources_ids]),

        "factual_correctness_Information_Provided_is_factual": "",
        "factual_correctness_Information_provided_contains_factual_inaccuracies.": "",

        "completeness_of_response_Complete_response_addresses_all_aspects": "",
        "completeness_of_response_Partially_complete_response": "",
        "completeness_of_response_Key_information_is_missing": "",

        "helpfulness_of_reccomendation_Helpful and reasonable recommendation with actionable insights": "",
        "helpfulness_of_reccomendation_Partially_helpful_but_lacks_clarity_or_relevance": "",
        "helpfulness_of_reccomendation_Not_helpful_at_all": ""
    }

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# =========================
# Run / Display Logic
# =========================

if run:
    if not chroma_path or not os.path.isdir(chroma_path):
        st.error(f"Chroma path does not exist or is not a directory: {chroma_path}")
        st.stop()

    # Open DB
    embedding_model = os.path.basename(os.path.normpath(chroma_path))
    db = Chroma(
        collection_name=collection_name,
        persist_directory=chroma_path,
        embedding_function=get_embedding_function(embedding_model),
    )

    # Retrieve
    results = db.similarity_search_with_score(query, k=10)

    # Metadata-aware reranking
    def boost_metadata_matches(results, query_text):
        boosted = []
        for doc, score in results:
            boost = 0
            for key in ["submitter", "source_doc", "section"]:
                value = doc.metadata.get(key, "")
                if value and query_text.lower() in value.lower():
                    boost += 0.15  # adjust boost weight as needed
            boosted.append((doc, score - boost))  # lower score = higher rank
        return sorted(boosted, key=lambda x: x[1])

    results = boost_metadata_matches(results, query)

    if not results:
        st.warning("No relevant documents found for your query.")
        response_text = "No relevant context available."
        sources_table = []
    else:
        # Build context
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        from langchain.prompts import ChatPromptTemplate
        from langchain_ollama import OllamaLLM

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        model = OllamaLLM(model=llm_model)
        chain = prompt_template | model

        placeholder = st.empty()
        chunks = []
        for piece in chain.stream({"context": context_text, "question": query}):
            chunks.append(piece)
            placeholder.markdown("**Response:**\n\n" + "".join(chunks))
        response_text = "".join(chunks)

        # Build pretty sources table
        sources_table = build_sources_table(results)
        render_sources_nice(sources_table)

    # Show response if retrieval empty (to keep layout consistent)
    if not results:
        st.markdown("**Response:**\n\n" + response_text)

    # Log to CSV (optional)
    if log_csv:
        sources_ids = [r["doc_id"] for r in sources_table]
        log_to_csv(
            csv_path=log_csv,
            query=query,
            embedding_model=embedding_model,
            chroma_path=chroma_path,
            collection_name=collection_name,
            llm_model=llm_model,
            llm_output=response_text,
            sources_ids=sources_ids,
        )

    # Save to history (limit size to 200)
    st.session_state.history.append({
        "ts": datetime.utcnow().isoformat(),
        "query": query,
        "response": response_text,
        "sources": sources_table,
        "chroma_path": chroma_path,
        "collection_name": collection_name,
        "llm_model": llm_model,
        "embedding_model": embedding_model,
    })
    if len(st.session_state.history) > 200:
        st.session_state.history = st.session_state.history[-200:]

    st.session_state.selected_history_idx = None  # reset selection after new run
    st.success("Done.")

# If user clicked a history item, render it without re-running
if selected_snapshot and not run:
    st.info("Showing a previous result from history (not re-run).")
    st.markdown(f"**Query:** {selected_snapshot['query']}")
    st.markdown(f"**LLM:** `{selected_snapshot['llm_model']}`  |  **DB:** `{selected_snapshot['chroma_path']}`  |  **Collection:** `{selected_snapshot['collection_name']}`")
    st.markdown("**Response:**\n\n" + selected_snapshot["response"])
    render_sources_nice(selected_snapshot["sources"])
