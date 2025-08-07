# rag_engine.py


import os
import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_documents_from_folder(folder_path):
	"""
	go through all pdfs
	"""
	documents = []
	for filename in os.listdir(folder_path):
		if filename.lower().endswith(".pdf"):
			loader = PyPDFLoader(os.path.join(folder_path, filename))
			docs = loader.load()
			documents.extend(docs)
	return documents

def split_documents(documents, chunk_size=1200, chunk_overlap=200):
	"""
	Split each pdf into smaller pieces to help extract useful information
	"""
	
	splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap
	)
	return splitter.split_documents(documents)
	
def embed_documents(chunks):
	"""
	embed those small pieces from split_documents using sentence-transformets
	"""
	print(f"Received {len(chunks)} chunks")
	if not chunks:
		raise ValueError("No chunks received. Loading and splitting may be off.")

	print("model loading")
	embedding_model = HuggingFaceEmbeddings(
		model_name="sentence-transformers/all-MiniLM-L6-v2",
		model_kwargs={"device": "cuda"}
	)
	vectorstore = FAISS.from_documents(chunks, embedding_model)
	return vectorstore
