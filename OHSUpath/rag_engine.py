# rag_engine.py


import os
import multiprocessing
import torch
import time
import faiss
import fitz
import numpy as np
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.docstore import InMemoryDocstore


def get_thread_count(min_threads=8, reserve_threads=2):
    total_threads = multiprocessing.cpu_count()
    recommend = total_threads - reserve_threads
    if recommend < min_threads:
        return total_threads
    return recommend


def load_single_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            pages.append(Document(page_content=text, metadata={"source": pdf_path}))
        print(f"Loaded {len(pages)} pages from: {pdf_path}")
        return pages
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
        try:
            docs = load_single_pdf(pdf_path)
            processed_count += 1
            print(
                f"Progress: {processed_count}/{total_files} loaded ({total_files - processed_count} left)"
            )
            return docs
        except Exception as e:
            print(f"Failed to load {pdf_path}: {e}")
            return []

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
    print(f"Starting document splitting...")

    start_time = time.time()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunks = []
    with tqdm(total=len(documents), desc="Splitting Documents") as pbar:
        for doc in documents:
            doc_chunks = splitter.split_documents([doc])
            chunks.extend(doc_chunks)
            pbar.update(1)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Document splitting completed in {duration:.2f} seconds.")
    print(f"Split into {len(chunks)} chunks.")

    return chunks


def embed_documents(chunks):
    """
    embed those small pieces from split_documents using sentence-transformets
    """
    print(f"Received {len(chunks)} chunks")

    if not chunks:
        raise ValueError("No chunks received. Loading and splitting may be off.")

    print("model loading")
    start_time = time.time()

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cuda"},
    )

    print("pytorch GPU CUDA?", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Working on CUDA")
    else:
        print("Not working on CUDA")

    embedding_dim = 384
    index = faiss.IndexFlatL2(embedding_dim)
    documents_store = {}
    index_to_docstore_id = []

    with tqdm(total=len(chunks), desc="Embedding Chunks") as pbar:
        for i, chunk in enumerate(chunks):
            doc_id = str(i)
            document_text = chunk.page_content
            embedding = embedding_model.embed_documents([document_text])
            embedding_np = np.array(embedding, dtype=np.float32)

            if embedding_np.shape != (1, embedding_dim):
                raise ValueError(
                    f"Embedding shape {embedding_np.shape} is incorrect, expected (1, {embedding_dim})"
                )

            index.add(embedding_np)
            documents_store[doc_id] = chunk
            index_to_docstore_id.append(doc_id)
            pbar.update(1)

    docstore = InMemoryDocstore(documents_store)

    vectorstore = FAISS(
        index=index,
        embedding_function=embedding_model,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )

    duration = time.time() - start_time
    print(f"Model and vector store creation completed in {duration:.2f} seconds.")
    return vectorstore
