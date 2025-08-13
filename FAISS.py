import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

# Load CSV
df = pd.read_csv("lab_chunks.csv")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed all text chunks
embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)

# Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save index and metadata
faiss.write_index(index, "lab_index.faiss")
df.to_pickle("lab_metadata.pkl")  # save metadata with same row order
