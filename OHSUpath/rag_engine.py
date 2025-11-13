# rag_engine.py


import os
import multiprocessing
import torch
import time
import faiss
import fitz
import numpy as np
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from config import Config


def get_thread_count(cfg: Config) -> int:
    total_threads = multiprocessing.cpu_count()
    recommend = total_threads - cfg.runtime.reserve_threads
    if recommend < cfg.runtime.min_threads:
        return total_threads
    return recommend




def load_single_pdf(pdf_path: str, cfg: Config, pbar=None):
    """
    Load a single PDF and update per-page progress.
    """
    try:
        with fitz.open(pdf_path) as doc:
            pages = []
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text(cfg.paths.pdf_text_mode).strip()
                if len(text) < cfg.split.min_chars_per_page:
                    continue
                pages.append(Document(page_content=text, metadata={"source": pdf_path}))

                if pbar is not None:
                    pbar.update(1)

        # print(f"Loaded {len(pages)} pages from: {pdf_path}")
        return pages
    except Exception as e:
        print(f"Failed to load {pdf_path}: {e}")
        return []


def load_documents_from_folder(folder_path: str, max_workers: int | None, cfg: Config):
    """
    Go through all PDFs, count total pages, and show load documents progress.
    """
    print(">>> Starting document loading...")

    start_time = time.time()

    folder_path = str(Path(folder_path))
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return []

    exts = {ext.lower() for ext in (cfg.paths.allowed_extensions or [".pdf"])}
    file_paths = []
    total_pages = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in exts):
                full_path = os.path.join(root, file)
                file_paths.append(full_path)

                try:
                    with fitz.open(full_path) as doc:
                        total_pages += doc.page_count
                except Exception as e:
                    print(f"Failed to read page count for {full_path}: {e}")

    total_files = len(file_paths)
    print(
        f"Found {total_files} files matching {sorted(exts)} with {total_pages} total pages."
    )

    if max_workers is None:
        max_workers = cfg.runtime.max_workers or get_thread_count(cfg)

    documents = []
    processed_count = 0

    with tqdm(total=total_pages, desc="Loading PDF Pages") as pbar:

        def wrapped_loader(path_):
            nonlocal processed_count
            docs = load_single_pdf(path_, cfg, pbar)
            processed_count += 1
            return docs

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for docs in executor.map(wrapped_loader, file_paths):
                documents.extend(docs)

    duration = time.time() - start_time
    print(f"Document loading completed in {duration:.2f} seconds. Total documents: {len(documents)}")

    return documents


def split_documents(documents, cfg: Config):
    """
    Split each pdf into smaller pieces to help extract useful information
    """
    print(">>> Starting document splitting...")
    start_time = time.time()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.split.chunk_size,
        chunk_overlap=cfg.split.chunk_overlap,
    )

    chunks = []
    with tqdm(total=len(documents), desc="Splitting Documents") as pbar:
        for doc in documents:
            chunks.extend(splitter.split_documents([doc]))
            pbar.update(1)

    duration = time.time() - start_time
    print(f"Document splitting completed in {duration:.2f} seconds. Total chunks: {len(chunks)}")

    return chunks


def embed_documents(chunks, cfg: Config):
    """
    embed those small pieces from split_documents using sentence-transformets
    """
    print(f">>> Starting Sentence-transformer embedding...")
    if not chunks:
        raise ValueError("No chunks received. Loading and splitting may be off.")

    start_time = time.time()

    device = cfg.runtime.device
    if device.startswith("cuda") and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"

    embedding_model = HuggingFaceEmbeddings(
        model_name=cfg.embedding.model_name,
        model_kwargs={"device": device},
    )

    


    embedding_dim = cfg.embedding.embedding_dim
    index = faiss.IndexFlatL2(embedding_dim)

    documents_store = {}
    index_to_docstore_id = []

    with tqdm(total=len(chunks), desc="Embedding Chunks") as pbar:
        for i, chunk in enumerate(chunks):
            doc_id = str(i)
            text = chunk.page_content
            embedding = embedding_model.embed_documents([text])
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
