import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load the Qwen embedding model
# -----------------------------
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    trust_remote_code=True,
    tokenizer_kwargs={"padding_side": "left"},
)

# -----------------------------
# Load chunks from JSONL
# -----------------------------
with open("ragflow_chunks.jsonl", "r") as f:
    chunks = [json.loads(line) for line in f]

texts = [c["text"] for c in chunks]
print(f"Loaded {len(texts)} chunks")

# -----------------------------
# Embed documents (chunks)
# -----------------------------
doc_embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    batch_size=16,   # try 8, 16, or 32 depending on memory
    show_progress_bar=True
)
print(f"Embeddings shape: {doc_embeddings.shape}")  # (num_chunks, embedding_dim)

# -----------------------------
# Save embeddings + metadata
# -----------------------------
np.save("ragflow_embeddings.npy", doc_embeddings)

with open("ragflow_metadata.json", "w") as f:
    json.dump(chunks, f)

print("Saved embeddings to ragflow_embeddings.npy and metadata to ragflow_metadata.json")

# -----------------------------
# Example query
# -----------------------------
query = "What is the SMAD4 immunostain result?"
query_emb = model.encode([query], prompt_name="query", convert_to_numpy=True)

sims = cosine_similarity(query_emb, doc_embeddings)[0]
top_idx = sims.argsort()[::-1][:5]

print("\nTop 5 results:")
for rank, idx in enumerate(top_idx):
    print(f"{rank+1}. {chunks[idx]['text']} | score={sims[idx]:.4f}")