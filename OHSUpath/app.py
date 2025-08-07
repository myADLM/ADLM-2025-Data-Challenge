#app.py

import streamlit as st 
from langchain.chains import RetrievalQA 
from langchain_community.llms import Ollama 
from rag_engine import load_documents_from_folder, split_documents, embed_documents

st.title("AI tool name holder")

@st.cache_resource
def setup_qa():
	docs = load_documents_from_folder("data/LabDocs")
	chunks = split_documents(docs)
	vectordb = embed_documents(chunks)

	llm = Ollama(model="deepseek-coder")
	qa_chain = RetrievalQA.from_chain_type(
		llm=llm,
		retriever=vectordb.as_retriever(),
		return_source_documents=True
	)
	return qa_chain

qa = setup_qa()

query = st.text_input("***Enter your question***")

if query:
	with st.spinner("analysing..."):
		result = qa({"query":query})
		st.write("***Answer***")
		st.write(result["result"])

		st.write("***sourses***")
		for doc in result["Source_documents"]:
			st.markdown(f"***FILENAME:*** {doc.metadata.get('source')}")
			st.write(doc.page_content[:500]+"...")