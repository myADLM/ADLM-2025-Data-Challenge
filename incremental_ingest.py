import os
import json
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Paths / constants
DOCS_DIR = 'LabDocs'
METADATA_PATH = 'lab_metadata.pkl'
INDEX_PATH = 'lab_index.faiss'
CHUNKS_CSV = 'lab_chunks.csv'
VECTOR_INDEX_PATH = 'vector_index.json'  # stores next available vector id
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def extract_text_from_pdf(pdf_path):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() or '' for page in reader.pages)
    except Exception as e:
        print(f"Failed to extract {pdf_path}: {e}")
        return ""


def load_metadata():
    if os.path.exists(METADATA_PATH):
        return pd.read_pickle(METADATA_PATH)
    return pd.DataFrame(columns=["filename", "chunk_id", "text", "vector_id"])


def save_metadata(df):
    df.to_pickle(METADATA_PATH)
    df.to_csv(CHUNKS_CSV, index=False)


def load_vector_index():
    if os.path.exists(VECTOR_INDEX_PATH):
        with open(VECTOR_INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"next_id": 1}


def save_vector_index(d):
    with open(VECTOR_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(d, f)


def ensure_index_with_idmap(dimension=None):
    """Load existing index or create a new IndexFlatL2 wrapped with IndexIDMap2."""
    if os.path.exists(INDEX_PATH):
        idx = faiss.read_index(INDEX_PATH)
        # If it's already an IDMap2, return it. Otherwise wrap existing base index into IDMap2.
        if isinstance(idx, faiss.IndexIDMap2):
            return idx
        else:
            base = idx
            idmap = faiss.IndexIDMap2(base)
            return idmap
    else:
        if dimension is None:
            raise ValueError("Dimension must be provided when creating a new index")
        base = faiss.IndexFlatL2(dimension)
        idmap = faiss.IndexIDMap2(base)
        return idmap


def migrate_metadata_to_ids(metadata, model, vec_index):
    """If metadata lacks vector_id, embed all texts and create index with IDs.
    Returns (index, metadata, vec_index)
    """
    texts = metadata['text'].tolist()
    if not texts:
        # Nothing to migrate — just return empty index
        return ensure_index_with_idmap(dimension=384), metadata, vec_index

    print("Migrating existing metadata to use vector IDs (this may take a while)...")
    embeddings = model.encode(texts, show_progress_bar=True)
    emb_np = np.array(embeddings).astype('float32')
    dim = emb_np.shape[1]
    index = ensure_index_with_idmap(dimension=dim)

    n = emb_np.shape[0]
    start_id = vec_index.get('next_id', 1)
    ids = np.arange(start_id, start_id + n, dtype='int64')
    index.add_with_ids(emb_np, ids)

    # Assign vector_ids to metadata in row order 
    metadata = metadata.reset_index(drop=True)
    metadata['vector_id'] = ids.tolist()
    vec_index['next_id'] = int(start_id + n)
    save_vector_index(vec_index)
    save_metadata(metadata)
    faiss.write_index(index, INDEX_PATH)
    print(f"Migration complete — assigned {n} vector IDs.")
    return index, metadata, vec_index


def remove_vectors_by_ids(index, ids):
    if len(ids) == 0:
        return 0
    ids_np = np.array(ids, dtype='int64')
    # IndexIDMap2 supports remove_ids
    try:
        index.remove_ids(ids_np)
        return len(ids)
    except Exception as e:
        print(f"Failed to remove ids via index.remove_ids: {e}")
        raise


def main(detect_deleted=True, add_new=True):
    # Load metadata and vector index
    metadata = load_metadata()
    vec_index = load_vector_index()
    model = SentenceTransformer(EMBEDDING_MODEL)

    if 'vector_id' not in metadata.columns or metadata['vector_id'].isnull().any():
        index, metadata, vec_index = migrate_metadata_to_ids(metadata, model, vec_index)
    else:
        try:
            index = ensure_index_with_idmap()
            if index.ntotal == 0 and len(metadata) > 0:
                print("Index missing vectors — rebuilding from metadata...")
                texts = metadata['text'].tolist()
                emb = model.encode(texts, show_progress_bar=True)
                emb_np = np.array(emb).astype('float32')
                ids = np.array(metadata['vector_id'].tolist(), dtype='int64')
                index.add_with_ids(emb_np, ids)
                faiss.write_index(index, INDEX_PATH)
        except Exception:
            if len(metadata) > 0:
                texts = metadata['text'].tolist()
                emb = model.encode(texts, show_progress_bar=True)
                emb_np = np.array(emb).astype('float32')
                dim = emb_np.shape[1]
                index = ensure_index_with_idmap(dimension=dim)
                ids = np.array(metadata['vector_id'].tolist(), dtype='int64')
                index.add_with_ids(emb_np, ids)
                faiss.write_index(index, INDEX_PATH)
            else:
                index = ensure_index_with_idmap(dimension=384)

    # Detect deleted files on disk and remove their vectors
    existing_files_on_disk = set()
    for root, _, files in os.walk(DOCS_DIR):
        for f in files:
            if f.lower().endswith('.pdf'):
                existing_files_on_disk.add(f)

    removed_total = 0
    if detect_deleted and not metadata.empty:
        filenames_in_meta = set(metadata['filename'].unique())
        deleted_files = [fn for fn in filenames_in_meta if fn not in existing_files_on_disk]
        if deleted_files:
            print(f"Found {len(deleted_files)} deleted files: {deleted_files}")
            ids_to_remove = metadata[metadata['filename'].isin(deleted_files)]['vector_id'].tolist()
            # Remove from index
            removed_total = remove_vectors_by_ids(index, ids_to_remove)
            # Drop rows from metadata
            metadata = metadata.loc[~metadata['filename'].isin(deleted_files)].reset_index(drop=True)
            save_metadata(metadata)
            faiss.write_index(index, INDEX_PATH)
            print(f"Removed {removed_total} vectors associated with deleted files.")
        else:
            print("No deleted files detected.")

    # Add new files found on disk that are not present in metadata
    if add_new:
        filenames_in_meta = set(metadata['filename'].unique())
        new_files = []
        for root, _, files in os.walk(DOCS_DIR):
            for f in files:
                if f.lower().endswith('.pdf') and f not in filenames_in_meta:
                    new_files.append(os.path.join(root, f))

        if new_files:
            print(f"Adding {len(new_files)} new files...")
            all_new_chunks = []
            all_new_embs = []
            new_ids = []
            for file_path in new_files:
                print(f"Processing {file_path}")
                text = extract_text_from_pdf(file_path)
                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    all_new_chunks.append({
                        'filename': os.path.basename(file_path),
                        'chunk_id': i,
                        'text': chunk
                    })
                    emb = model.encode(chunk)
                    all_new_embs.append(emb)

            if all_new_embs:
                emb_np = np.array(all_new_embs).astype('float32')
                n_new = emb_np.shape[0]
                start_id = int(vec_index.get('next_id', 1))
                ids = np.arange(start_id, start_id + n_new, dtype='int64')
                index.add_with_ids(emb_np, ids)
                # update vector index counter
                vec_index['next_id'] = int(start_id + n_new)
                save_vector_index(vec_index)

                # append metadata rows with vector_ids
                new_df = pd.DataFrame(all_new_chunks)
                new_df['vector_id'] = ids.tolist()
                metadata = pd.concat([metadata, new_df], ignore_index=True)
                save_metadata(metadata)
                faiss.write_index(index, INDEX_PATH)
                print(f"Added {n_new} new chunks from {len(new_files)} files.")
        else:
            print("No new files to add.")


if __name__ == '__main__':
    # Run migration + delete detection + add new files
    main(detect_deleted=True, add_new=True)
