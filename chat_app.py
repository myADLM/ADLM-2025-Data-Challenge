import streamlit as st
from ask import ask_question_with_openai
import incremental_ingest
import shutil
import os
import tempfile
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# Sidebar with logo and info 
st.sidebar.title("LabDocs Chat Assistant")
st.sidebar.markdown("""
**Welcome!**

Ask any question about lab procedures. Answers are based only on the provided documents.
If you have a follow-up question, just ask!
""")
if st.sidebar.button("Clear Chat 🗑️"):
    st.session_state.history = []

# Main area 

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem;}
        .stChatMessage {border-radius: 18px; margin-bottom: 0.5rem;}
        .stChatMessage.user {
            background-color: #e6f0fa !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧪 LabDocs Chat Assistant 🧪")
st.divider()

# Chat history 
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    avatar = "🔍" if msg["role"] == "assistant" else "👩‍🔬"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat input 
user_input = st.chat_input("Type your question and press Enter...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    # Show spinner while waiting for answer
    with st.spinner("LabDocs AI is thinking..."):
        history_for_qa = [m for m in st.session_state.history if m["role"] in ("user", "assistant")][:-1]
        answer = ask_question_with_openai(user_input, history=history_for_qa)
    st.session_state.history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🧑‍🔬"):
        st.markdown(answer)

# Password-protected file upload 
UPLOAD_PASSWORD = "admin"  # Change accordingly

with st.sidebar:
    st.markdown("---")
    st.markdown("#### 🔒 Admin Upload")
    upload_access = False
    password = st.text_input("Enter upload password", type="password")
    if password == UPLOAD_PASSWORD:
        upload_access = True
        st.success("Upload access granted.")
    elif password:
        st.error("Incorrect password.")

    if upload_access:
        uploaded_file = st.file_uploader("Upload a PDF to add to the knowledge base", type=["pdf"])
        if uploaded_file is not None:
            # Save uploaded file to LabDocs (persist it) and ask user to run incremental ingest
            os.makedirs('LabDocs', exist_ok=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            dest_path = os.path.join('LabDocs', uploaded_file.name)
            # Move temp file into LabDocs (overwrite if exists)
            try:
                shutil.move(tmp_path, dest_path)
            except Exception:
                # fallback to copy
                shutil.copy(tmp_path, dest_path)
                os.remove(tmp_path)

            st.success(f"Saved {uploaded_file.name} to LabDocs/. To update the vector index, click 'Run incremental ingest' below.")

            if st.button("Run incremental ingest now"):
                with st.spinner("Running incremental ingest (this may take a while)..."):
                    try:
                        incremental_ingest.main(detect_deleted=True, add_new=True)
                        st.success("Incremental ingest completed. Index and metadata updated.")
                    except Exception as e:
                        st.error(f"Incremental ingest failed: {e}")

try:
    metadata = pd.read_pickle("lab_metadata.pkl")
    num_docs = metadata['filename'].nunique()
    num_chunks = len(metadata)
except Exception:
    num_docs = num_chunks = 0

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

# Increment query count on each user question
if user_input:
    st.session_state.query_count += 1

# Place admin dashboard at the end of the sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### Doc Dashboard")
    st.markdown(f"**Documents:** {num_docs}")
    st.markdown(f"**Chunks:** {num_chunks}")
    st.markdown(f"**User Queries (this session):** {st.session_state.query_count}")

# Download chat history button 
import io

def format_chat_history(history):
    lines = []
    for msg in history:
        role = "You" if msg["role"] == "user" else "LabDocs AI"
        lines.append(f"{role}: {msg['content']}")
    return "\n\n".join(lines)

if st.session_state.history:
    chat_txt = format_chat_history(st.session_state.history)
    st.sidebar.download_button(
        label="Download Chat History",
        data=chat_txt,
        file_name="labdocs_chat_history.txt",
        mime="text/plain"
    )
