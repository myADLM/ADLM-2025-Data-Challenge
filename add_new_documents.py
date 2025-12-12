import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle


DOCS_DIR = 'LabDocs'  
METADATA_PATH = 'lab_metadata.pkl'
INDEX_PATH = 'lab_index.faiss'
CHUNKS_CSV = 'lab_chunks.csv'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 500  # Adjust as needed
CHUNK_OVERLAP = 50  # Adjust as needed

# Chunk text 
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Extract text from PDF 
def extract_text_from_pdf(pdf_path):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() or '' for page in reader.pages)
    except Exception as e:
        print(f"Failed to extract {pdf_path}: {e}")
        return ""

# Load existing metadata and index 
if os.path.exists(METADATA_PATH):
    metadata = pd.read_pickle(METADATA_PATH)
else:
    metadata = pd.DataFrame(columns=["filename", "chunk_id", "text"])

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = None  # Will create if needed

# Find all documents 
all_files = []
for root, _, files in os.walk(DOCS_DIR):
    for f in files:
        if f.lower().endswith('.pdf'):
            all_files.append(os.path.join(root, f))

# Identify new documents 
existing_files = set(metadata['filename'].unique())
new_files = [f for f in all_files if os.path.basename(f) not in existing_files]

if not new_files:
    print("No new documents to add.")
    exit(0)

print(f"Found {len(new_files)} new documents.")

# Load embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

new_chunks = []
new_embeddings = []

for file_path in new_files:
    print(f"Processing {file_path}")
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        new_chunks.append({
            "filename": os.path.basename(file_path),
            "chunk_id": i,
            "text": chunk
        })
        new_embeddings.append(model.encode(chunk))

# Add new embeddings to FAISS index 
new_embeddings_np = np.vstack(new_embeddings)
if index is None:
    # Create a new index
    dimension = new_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(new_embeddings_np)
else:
    index.add(new_embeddings_np)

# Update metadata
metadata = pd.concat([metadata, pd.DataFrame(new_chunks)], ignore_index=True)
metadata.to_pickle(METADATA_PATH)
metadata.to_csv(CHUNKS_CSV, index=False)
faiss.write_index(index, INDEX_PATH)

print(f"Added {len(new_chunks)} new chunks from {len(new_files)} documents.")
print("Index and metadata updated!")
