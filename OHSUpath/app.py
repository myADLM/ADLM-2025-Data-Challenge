# app.py

import os
import streamlit as st
import numpy as np
from pathlib import Path
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from rag_engine import load_documents_from_folder, split_documents, embed_documents
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import load_config

# ------------------------------------------------------------
# CONFIGURATION MODE SWITCH
# True  = Use YAML + env variables + defaults in config.py
# False = Use ONLY env variables + defaults in config.py
# ------------------------------------------------------------
USE_YAML_CONFIG: bool = True  # True = use YAML, False = skip YAML


cfg = load_config(use_yaml=USE_YAML_CONFIG)


st.set_page_config(page_title=cfg.app.page_title)
st.title(cfg.app.title)


# Make Streamlit's cache sensitive to config changes
# by serializing the cfg object into a string key
def _cfg_key(c):
    # Serialization
    return (
        str(vars(c.paths))
        + str(vars(c.runtime))
        + str(vars(c.split))
        + str(vars(c.embedding))
        + str(vars(c.retriever))
        + str(vars(c.llm))
        + str(vars(c.app))
    )


@st.cache_resource(hash_funcs={type(cfg): lambda x: _cfg_key(x)})
def setup_qa(_cfg):
    docs = load_documents_from_folder(_cfg.paths.data_dir, None, _cfg)
    st.write(f"Loaded {len(docs)} documents from folder")

    if docs:
        st.write("Sample doc content:", docs[0].page_content[:100])
    else:
        st.write("No documents loaded")

    chunks = split_documents(docs, _cfg)
    vectordb = embed_documents(chunks, _cfg)
    retriever = vectordb.as_retriever(
        search_type=_cfg.retriever.search_type,
        search_kwargs={"k": _cfg.retriever.k},
    )

    if _cfg.llm.provider.lower() == "ollama":
        llm = Ollama(
            model=_cfg.llm.model, base_url=_cfg.llm.base_url, **(_cfg.llm.params or {})
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {_cfg.llm.provider}")

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=_cfg.llm.chain_type,
        retriever=retriever,
        return_source_documents=True,
    )

    return qa


qa = setup_qa(cfg)

if qa is None:
    st.warning("No documents found. Check 'paths.data_dir' in config.yaml.")
    st.stop()


query = st.text_input(cfg.app.ui.input_label)
if query:
    with st.spinner(cfg.app.ui.spinner_text):
        result = qa.invoke({"query": query})
        st.write("***Answer***")
        st.write(result["result"])

        st.write("***sources***")
        for doc in result["source_documents"]:
            st.markdown(f"***FILENAME:*** {doc.metadata.get('source')}")
            st.write(doc.page_content[:500] + "...")
