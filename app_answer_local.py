import os
import json
from pathlib import Path
import pickle
import re
from typing import List, Dict, Tuple

import streamlit as st
from rank_bm25 import BM25Okapi
from groq import Groq

INDEX_DIR = Path("index")
META_PATH = INDEX_DIR / "meta.jsonl"
BM25_PATH = INDEX_DIR / "bm25.pkl"

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

WORD_RE = re.compile(r"[A-Za-z0-9_]+")

@st.cache_resource(show_spinner=False)
def load_index():
    if not META_PATH.exists() or not BM25_PATH.exists():
        raise FileNotFoundError("Index missing. Please run build_index.py first.")
    # load meta lines lazily (positions)
    meta = []
    with META_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))
    with BM25_PATH.open("rb") as f:
        d = pickle.load(f)
    bm25: BM25Okapi = d["bm25"]
    return meta, bm25

def tokenize(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]

def retrieve(query: str, bm25: BM25Okapi, meta: List[Dict], top_k: int = 8) -> List[Tuple[int, float]]:
    tokens = tokenize(query)
    scores = bm25.get_scores(tokens)
    # get top_k indices
    top = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    # filter out empty/very low
    top = [(i, s) for i, s in top if s > 0]
    return top

def make_context(chunks: List[Dict]) -> str:
    # compact context with clear separators so the model can cite
    parts = []
    for c in chunks:
        header = f"[{c['file']} | page {c['page']}]"
        snippet = c["text"].strip().replace("\n", " ").strip()
        if len(snippet) > 1200:
            snippet = snippet[:1200] + " ..."
        parts.append(f"{header}\n{snippet}")
    return "\n\n---\n\n".join(parts)

def call_llm(client: Groq, model: str, question: str, context: str) -> str:
    # Keep prompt compact; instruct to cite using [file | page X]
    system = (
        "You are a precise assistant. Answer ONLY from the provided context. "
        "Include citations like [filename.pdf | page X] after each fact you use. "
        "If the answer is not in the context, say you couldn't find it."
    )
    user = f"Question:\n{question}\n\nContext:\n{context}"
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content": system},
            {"role":"user","content": user}
        ],
        temperature=0.1,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()

def main():
    st.set_page_config(page_title="LabDocs (Groq)", page_icon="🔎", layout="wide")
    st.title("🔎 LabDocs RAG (Groq, multi-PDF)")
    st.caption("Ask questions. The app retrieves top pages and the LLM answers with page-level citations.")

    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        st.error("GROQ_API_KEY is not set. In your terminal:  set GROQ_API_KEY=YOUR_KEY  (then restart)")
        st.stop()

    model = st.sidebar.selectbox(
        "Groq model",
        options=[
            "llama-3.3-70b-versatile",  # if you have access; otherwise use the 8B below
            "llama-3.1-8b-instant",     # safe default (free tier)
            "mixtral-8x7b-32768",       # larger, if available
        ],
        index=1
    )
    st.sidebar.write("Top-K retrieval controls")
    top_k = st.sidebar.slider("Retrieve top pages", 3, 20, 8)
    st.sidebar.caption("Index folder: ./index  |  PDFs: ./data_raw and ./data_ocr_done")

    try:
        meta, bm25 = load_index()
    except Exception as e:
        st.error(f"Failed to load index: {e}")
        st.stop()

    question = st.text_input("Ask a question about the documents:", value="")
    if st.button("Search") or (question and st.session_state.get("auto_search_once") is None):
        st.session_state["auto_search_once"] = True

    if question and st.session_state.get("auto_search_once"):
        with st.spinner("Retrieving..."):
            hits = retrieve(question, bm25, meta, top_k=top_k)
            if not hits:
                st.warning("No relevant pages found in the index.")
                return
            chosen = [meta[i] for i, _ in hits]
            context = make_context(chosen)
        with st.spinner("Calling Groq model..."):
            client = Groq(api_key=groq_key)
            try:
                answer = call_llm(client, model, question, context)
            except Exception as e:
                st.error(f"Groq call failed: {e}")
                return

        st.subheader("Answer")
        st.write(answer)

        st.subheader("Cited sources (pages)")
        for c in chosen:
            st.markdown(f"• **{c['file']} — page {c['page']}**")

        with st.expander("See retrieved context"):
            st.text(context)

if __name__ == "__main__":
    main()
