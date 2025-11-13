import os
import sys
import re
import shutil
import argparse
from typing import List
import subprocess
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from get_embedding_function import get_embedding_function

# --- Config ---
CHROMA_PATH = "chroma"
DATA_PATH = ["Markdown-Output/Synthetic_Procedures", "Markdown-Output/FDA"]
DEFAULT_BATCH_SIZE = 250
DEFAULT_PERSIST_EVERY = 10
CHAR_CHUNK_SIZE = 500
CHAR_CHUNK_OVERLAP = 50
MAX_SAFE_BATCH = 250
COLLECTION_PREFIX = "ADLM_Embeddings_"

def _print_device_info():
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used", "--format=csv,nounits,noheader"]
        )
        print("✅ GPU detected via nvidia-smi:")
        print(output.decode().strip())
    except Exception:
        print("⚠️ Unable to detect GPU via nvidia-smi. Defaulting to CPU.")

def chunk_documents_by_characters(documents: List[Document], chunk_size: int = CHAR_CHUNK_SIZE, overlap: int = CHAR_CHUNK_OVERLAP) -> List[Document]:
    section_pattern = re.compile(
        r"<!-- section: ([\w\-]+) \| source: ([\w\-.]+) -->"
    )
    all_chunks = []

    for doc in documents:
        text = doc.page_content
        source = doc.metadata.get("source", "unknown")

        lines = text.splitlines()
        buffer = []
        char_count = 0
        current_section = "Unlabeled"
        current_source = source
        found_section = False

        def flush_chunk():
            nonlocal buffer, char_count
            if buffer:
                chunk_text = "\n".join(buffer).strip()
                all_chunks.append(Document(
                    page_content=chunk_text,
                    metadata={
                        "doc_id": source,
                        "source": current_source,
                        "section_type": current_section
                    }
                ))
                buffer.clear()
                char_count = 0

        for line in lines:
            match = section_pattern.match(line.strip())
            if match:
                flush_chunk()
                current_section = match.group(1)
                current_source = match.group(2)
                found_section = True
                buffer.append(line)
                char_count += len(line)
            else:
                buffer.append(line)
                char_count += len(line)
                if char_count >= chunk_size:
                    flush_chunk()

        flush_chunk()

        # Fallback: if no section tags were found, re-chunk the entire document
        if not found_section and all_chunks == []:
            for i in range(0, len(text), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size]
                all_chunks.append(Document(
                    page_content=chunk_text.strip(),
                    metadata={
                        "doc_id": source,
                        "source": source,
                        "section_type": "Unlabeled"
                    }
                ))

    return all_chunks

# --- Chunk ID Assignment ---
def calculate_chunk_ids(chunks: list[Document]) -> list[Document]:
    doc_chunk_counts = {}

    for chunk in chunks:
        if chunk.metadata is None:
            chunk.metadata = {}

        doc_id = chunk.metadata.get("doc_id", "unknown")
        section = chunk.metadata.get("section_type", "Uncategorized")
        if section is None:
            section = "Uncategorized"

        key = f"{doc_id}:{section.lower().replace(' ', '_')}"
        index = doc_chunk_counts.get(key, 0)
        chunk.metadata["id"] = f"{key}:{index}"
        doc_chunk_counts[key] = index + 1

    return chunks

# --- Chroma DB Setup ---
def _build_collection_name(model_name: str) -> str:
    return f"{COLLECTION_PREFIX}{model_name.replace(':', '_')}"

def _create_chroma_db(model_name: str) -> Chroma:
    model_db_path = os.path.join(CHROMA_PATH, model_name.replace(":", "_"))
    return Chroma(
        collection_name=_build_collection_name(model_name),
        persist_directory=model_db_path,
        embedding_function=get_embedding_function(model_name),
    )

# --- Ollama Model Check ---
def is_ollama_model_available(model_name: str) -> bool:
    base_name = model_name.split(":")[0]
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("❌ Ollama CLI not found. Install from https://ollama.com and ensure it's on your PATH.")
        return False
    except subprocess.CalledProcessError:
        print("❌ Failed to query Ollama. Is the Ollama service running?")
        return False
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    available_models = {line.split()[0].split(":")[0] for line in lines[1:]}
    if base_name in available_models:
        print(f"✅ Ollama model '{model_name}' is downloaded locally.")
        return True
    else:
        print(f"⚠️  Ollama model '{model_name}' is NOT downloaded.")
        print(f"💡 To download:  ollama pull {model_name}")
        return False

# --- Document Loading ---
def load_documents() -> List[Document]:
    all_docs = []
    for dir_path in DATA_PATH:
        loader = DirectoryLoader(
            dir_path,
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
        )
        docs = loader.load()
        print(f"📄 Loaded {len(docs):,} documents from {dir_path}")
        all_docs.extend(docs)
    return all_docs

# --- Chroma Upsert ---
def add_to_chroma(chunks: List[Document], model_name: str, batch_size: int = DEFAULT_BATCH_SIZE, persist_every: int = DEFAULT_PERSIST_EVERY):
    model_db_path = os.path.join(CHROMA_PATH, model_name.replace(":", "_"))
    collection_name = f"{COLLECTION_PREFIX}{model_name.replace(':', '_')}"

    db = Chroma(
        collection_name=collection_name,
        persist_directory=model_db_path,
        embedding_function=get_embedding_function(model_name),
    )

    chunks_with_ids = calculate_chunk_ids(chunks)
    print("🔍 Checking existing documents in Chroma...")
    existing_items = db.get(include=[], limit=None)
    existing_ids = set(existing_items.get("ids", []))
    print(f"🔍 Number of existing documents in DB ({model_name}): {len(existing_ids):,}")

    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]
    if not new_chunks:
        print(f"✅ No new documents to add for {model_name}")
        return

    print(f"👉 Adding new documents for {model_name}: {len(new_chunks):,}")
    if batch_size > MAX_SAFE_BATCH:
        print(f"⚠️ Requested batch_size={batch_size} > {MAX_SAFE_BATCH}. Using {MAX_SAFE_BATCH}.")
        batch_size = MAX_SAFE_BATCH

    new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
    total = len(new_chunks)
    batches = (total + batch_size - 1) // batch_size

    print(f"🚀 Starting embedding of {total} chunks in {batches} batches (batch size: {batch_size})")

    try:
        for b in range(batches):
            start = b * batch_size
            end = min(start + batch_size, total)
            batch_docs = new_chunks[start:end]
            batch_ids = new_chunk_ids[start:end]

            print(f"🔢 Embedding batch {b + 1}/{batches} ({end - start} chunks)...")
            db.add_documents(batch_docs, ids=batch_ids)

            if persist_every > 0 and (b + 1) % persist_every == 0:
                print("💾 Persisting to disk...")

            print(f"✔ Upserted {end:,}/{total:,} docs (batch {b + 1}/{batches}, size {end - start})")

        print("✅ Finished adding documents.")
    except Exception as e:
        print(f"❌ Error during embedding: {e}")

def clear_database(model_name: str):
    model_db_path = os.path.join(CHROMA_PATH, model_name.replace(":", "_"))
    if os.path.exists(model_db_path):
        shutil.rmtree(model_db_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--model", type=str, default="llama3.1", help="Embedding model to use")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--persist-every", type=int, default=DEFAULT_PERSIST_EVERY)
    args = parser.parse_args()
    _print_device_info()

    if not is_ollama_model_available(args.model):
        print("❌ Exiting because the Ollama model is not available locally.")
        sys.exit(1)

    if args.reset:
        print("✨ Clearing Database")
        clear_database(args.model)

    print("📂 Loading markdown documents...")
    documents = load_documents()
    print(f"📄 Loaded {len(documents):,} documents")

    print("✂️ Splitting documents into chunks...")
    chunks = chunk_documents_by_characters(documents)
    print(f"🧩 Created {len(chunks):,} chunks")

    print("🚀 Starting embedding and upsert to Chroma...")
    add_to_chroma(chunks, args.model, batch_size=args.batch_size, persist_every=args.persist_every)

if __name__ == "__main__":
    main()

# EXAMPLE USAGE
# python .\py\populate_database_from_markdown_batch.py --model llama3.1
# python .\py\populate_database_from_markdown_batch.py --model nomic-embed-text

# You can also tune batch/persist:
# python embedding_utils\populate_database_from_markdown_batch.py --model nomic-embed-text
# python embedding_utils\populate_database_from_markdown_batch.py --model qwen3-embedding
