import streamlit as st
from ask import ask_question_with_openai
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

# File upload in sidebar 
with st.sidebar:
    uploaded_file = st.file_uploader("Upload new PDFs to add to the base", type=["pdf"])
    if uploaded_file is not None:
        # Save uploaded file to a temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        # Extract text
        reader = PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or '' for page in reader.pages)
        # Chunk text
        def chunk_text(text, chunk_size=500, overlap=50):
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunks.append(text[start:end])
                start += chunk_size - overlap
            return chunks
        chunks = chunk_text(text)
        # Load embedding model and index/metadata
        model = SentenceTransformer("all-MiniLM-L6-v2")
        metadata = pd.read_pickle("lab_metadata.pkl")
        index = faiss.read_index("lab_index.faiss")
        # Embed and add
        new_embeddings = []
        new_chunks = []
        for i, chunk in enumerate(chunks):
            new_chunks.append({
                "filename": uploaded_file.name,
                "chunk_id": i,
                "text": chunk
            })
            new_embeddings.append(model.encode(chunk))
        new_embeddings_np = np.vstack(new_embeddings)
        index.add(new_embeddings_np)
        # Update metadata
        metadata = pd.concat([metadata, pd.DataFrame(new_chunks)], ignore_index=True)
        metadata.to_pickle("lab_metadata.pkl")
        metadata.to_csv("lab_chunks.csv", index=False)
        faiss.write_index(index, "lab_index.faiss")
        st.success(f"Added {len(chunks)} chunks from {uploaded_file.name} to the knowledge base!")
        os.remove(tmp_path)

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
