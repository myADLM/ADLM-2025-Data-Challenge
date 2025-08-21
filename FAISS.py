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


# Build FAISS IVF index for faster approximate search
dimension = embeddings.shape[1]
nlist = 100  # number of clusters (can tune, e.g. sqrt(num_vectors))
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)

# Train the index (required for IVF)
embeddings_np = np.array(embeddings)
index.train(embeddings_np)
index.add(embeddings_np)

# Save index and metadata
faiss.write_index(index, "lab_index.faiss")
df.to_pickle("lab_metadata.pkl")  # save metadata with same row order
