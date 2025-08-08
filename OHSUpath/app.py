# app.py

import streamlit as st
import numpy as np
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from rag_engine import load_documents_from_folder, split_documents, embed_documents
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

st.title("AI tool name holder")


@st.cache_resource
def setup_qa():
    docs = load_documents_from_folder("data/LabDocs", None)
    print(f"Loaded {len(docs)} documents from folder")

    if docs:
        print("Sample doc content:", docs[0].page_content[:100])
    else:
        print("No documents loaded")
    chunks = split_documents(docs)
    vectordb = embed_documents(chunks)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    llm = Ollama(model="deepseek-r1-8b-int8")
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    return qa


qa = setup_qa()

query = st.text_input("***Enter your question***")

if query:
    with st.spinner("analysing..."):

        result = qa.invoke({"query": query})

        st.write("***Answer***")
        st.write(result["result"])

        st.write("***sources***")
        for doc in result["source_documents"]:
            st.markdown(f"***FILENAME:*** {doc.metadata.get('source')}")
            st.write(doc.page_content[:500] + "...")
