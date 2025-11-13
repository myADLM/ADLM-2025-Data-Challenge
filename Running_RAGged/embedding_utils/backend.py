import os
from typing import Dict, Iterable, Iterator, List, Tuple, Optional

from click import prompt

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function
import streamlit as st

# ---- Hardcoded parameters ----
CHROMA_PATH = "chroma/all-minilm"
COLLECTION_NAME = "ADLM_Embeddings_all-minilm"
LLM_MODEL = "gemma3"
TOP_K = 5
MAX_CONTEXT_CHARS = 100_000
DOCS_DIR = "docs/Markdown-Output"

# Serve that folder as static files
st.markdown(
    f"""
    <script>
    window.config = {{
        baseUrl: '{DOCS_DIR}'
    }}
    </script>
    """,
    unsafe_allow_html=True,
)

PROMPT_TEMPLATE = """
Answer the question using the context below if relevant.
If the context doesn’t contain the answer, respond 'Context not found.'

{context}

---

Answer the question based on the above context: {question}
""".strip()

# ---- Stub: will find or link local files later ----

# def find_relevant_files(citation: dict) -> dict:
#     """
#     Placeholder for your later logic to attach URLs/paths to citations.
#     Example (when implemented):
#         if "title" in citation:
#             citation["path"] = f"docs/{citation['title']}.pdf"
#     Attach a local file path to the citation based on metadata.
#     """
#     return citation  # currently no-op

"""
def find_relevant_files(citation: dict) -> dict:

   # Attach a local file path to the citation based on metadata.

    title = citation.get("title")
    if title:
        # Construct a likely filename (adjust extension if needed)
        candidate = os.path.join(DOCS_DIR, f"{title}.pdf")
        if os.path.exists(candidate):
            citation["path"] = candidate
        else:
            # Optional: fallback for lowercase/underscore versions
            candidate_alt = os.path.join(DOCS_DIR, f"{title.replace(' ', '_')}.pdf")
            if os.path.exists(candidate_alt):
                citation["path"] = candidate_alt
            else:
                citation["path"] = None
    return citation"""

def _try_candidate(path: Optional[str]) -> Optional[str]:
    """
    Return the normalized absolute path if the given path exists on disk.
    Used to verify metadata-provided file paths (like 'source' or 'path').
    """
    if not path:
        return None
    path = os.path.normpath(path)
    return path if os.path.exists(path) else None


def _glob_like(root: str, stem: str) -> Optional[str]:
    """
    Recursively search the given directory for a file whose stem (filename
    without extension) matches the provided 'stem'.
    Used as a fallback when the metadata doesn't contain an explicit path.
    """
    exts = (".pdf", ".md", ".html", ".htm", ".docx", ".txt")
    if not os.path.isdir(root):
        return None
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            name, ext = os.path.splitext(fn)
            if name == stem and ext.lower() in exts:
                candidate = os.path.join(dirpath, fn)
                if os.path.exists(candidate):
                    return candidate
    return None


def _as_file_url(path: str) -> str:
    """
    Convert a local filesystem path into a 'file://' URL that Streamlit can
    render as a clickable hyperlink.
    (Windows paths get triple slashes and forward slashes.)
    """
    abspath = os.path.abspath(path)
    if os.name == "nt":
        return "file:///" + abspath.replace("\\", "/")
    return "file://" + abspath


def find_relevant_files(citation: dict) -> dict:
    """
    Given a citation dictionary (from LangChain/Chroma metadata),
    try to attach a valid local file path and a clickable file:// URL.

    Resolution order:
      1. Direct metadata keys like 'path', 'source', or 'file_path'
      2. Filename matching using the document title inside DOCS_DIR
      3. Fallback to None if nothing found
    """
    meta = citation or {}

    # 1️⃣ Direct metadata path candidates
    for key in ("path", "file_path", "filepath", "source"):
        p = _try_candidate(meta.get(key))
        if p:
            citation["path"] = p
            citation.setdefault("url", _as_file_url(p))
            return citation

    # 2️⃣ Try guessing from title-based filenames
    title = meta.get("title")
    if title:
        p = _glob_like(DOCS_DIR, os.path.splitext(title)[0])
        if not p:
            # Try common variations (underscores/spaces)
            alt_stems = {
                title.replace(" ", "_"),
                title.replace("_", " "),
                title.strip(),
            }
            for stem in alt_stems:
                p = _glob_like(DOCS_DIR, os.path.splitext(stem)[0])
                if p:
                    break
        if p:
            citation["path"] = p
            citation.setdefault("url", _as_file_url(p))
            return citation

    # 3️⃣ Give up gracefully
    citation["path"] = None
    citation.setdefault("url", None)
    return citation

# ---- Internals ----
_db = None
_prompt_tmpl = None
_model = None

def _ensure_db() -> Chroma:
    global _db
    if _db is not None:
        return _db
    if not os.path.isdir(CHROMA_PATH):
        raise RuntimeError(f"Chroma path not found: {CHROMA_PATH}")
    embedding_model = os.path.basename(os.path.normpath(CHROMA_PATH))
    _db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(embedding_model),
    )
    return _db

def _ensure_chain() -> Tuple[ChatPromptTemplate, OllamaLLM]:
    global _prompt_tmpl, _model
    if _prompt_tmpl is None:
        _prompt_tmpl = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    if _model is None:
        _model = OllamaLLM(model=LLM_MODEL)
    return _prompt_tmpl, _model


# ---- Public API ----
def query_stream(prompt: str) -> Tuple[Iterable[str], List[Dict]]:
    db = _ensure_db()

    try:
        results = db.similarity_search_with_score(prompt, k=TOP_K)
        # print("Results returned:", results)
    except Exception as e:
        # Capture 'e' as a default argument in the inner function
        def _err(exc=e) -> Iterator[str]:
            yield f"Retrieval error: {exc}"
        return _err(), []

    if not results:
        def _noctx() -> Iterator[str]:
            yield "No relevant context available."
        return _noctx(), []

    # Build context and citations
    context_parts: List[str] = []
    citations: List[Dict] = []
    used = 0

    for rank, (doc, score) in enumerate(results, start=1):
        # Extract partial content for prompt context
        txt = doc.page_content or ""
        if used >= MAX_CONTEXT_CHARS:
            break
        take = min(len(txt), MAX_CONTEXT_CHARS - used)
        context_parts.append(txt[:take])
        used += take

        # Create citation metadata for each retrieved doc
        meta = dict(doc.metadata or {})
        cite = {
            "rank": rank,
            "title": meta.get("title") or meta.get("source") or f"doc_{rank}",
            "url": meta.get("url"),
            "path": meta.get("path") or meta.get("file_path") or meta.get("filepath") or meta.get("source"),
            "kind": meta.get("kind") or meta.get("type"),
            "section": meta.get("section") or meta.get("page") or meta.get("chunk"),
            "score": float(score) if score is not None else None,
        }

        # Copy any remaining metadata fields that might be useful later
        for k, v in meta.items():
            if k not in cite:
                cite[k] = v

        # 🔗 Try to attach a real file path and clickable URL
        cite = find_relevant_files(cite)
        citations.append(cite)

    # Merge all retrieved text chunks into a single model context
    context_text = "\n\n---\n\n".join(context_parts)
    prompt_tmpl, model = _ensure_chain()
    chain = prompt_tmpl | model

    def _gen() -> Iterator[str]:
        for piece in chain.stream({"context": context_text, "question": prompt}):
            yield str(piece)
    return _gen(), citations
    # citations
