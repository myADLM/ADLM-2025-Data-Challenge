# rag_engine.py


import os
import multiprocessing
import torch
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


def get_thread_count (min_threads = 8, reserve_threads = 2):
	total_threads = multiprocessing.cpu_count()
	recommend = total_threads-reserve_threads;
	if recommend < min_threads:
		return total_threads
	return recommend

def load_single_pdf(pdf_path):
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} pages from: {pdf_path}")
        return docs
    except Exception as e:
        print(f"Failed to load {pdf_path}: {e}") 
        return []


def load_documents_from_folder(folder_path, max_workers=None):
    """
    go through all pdfs
    """
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return []

    pdf_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                pdf_paths.append(full_path)

    total_files = len(pdf_paths)
    print(f"Found {total_files} PDF files.")

    # Set number of processes
    if max_workers is None:
        max_workers = get_thread_count()

    documents = []
    processed_count = 0

    def wrapped_loader(pdf_path):
        nonlocal processed_count
        docs = load_single_pdf(pdf_path)
        processed_count += 1
        print(f"Progress: {processed_count}/{total_files} loaded ({total_files - processed_count} left)")
        return docs

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(wrapped_loader, pdf_paths)
        for docs in results:
            documents.extend(docs)

    print(f"Total documents loaded: {len(documents)}")
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
	print("pytorch GPU CUDA?", torch.cuda.is_available())
	if torch.cuda.is_available():
		print("Working on CUDA")
	else:
		print("Not working on CUDA")
	vectorstore = FAISS.from_documents(chunks, embedding_model)
	return vectorstore
