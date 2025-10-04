import faiss
import numpy as np
from numpy.typing import NDArray

from app.src.util.open_ai_api import OpenAIAPI


class VectorSearch:
    def __init__(self, embeddings: NDArray[np.float32]):
        print("Initializing VectorSearch")
        # Soft failure for OpenAIAPI
        try:
            self.embedder = OpenAIAPI()
        except Exception as e:
            print(f"Error initializing OpenAIAPI: {e}")
            self.embedder = None

        # embeddings should already be in the correct shape (n_samples, n_features)

        print(f"Embeddings shape: {embeddings.shape}")
        embeddings_f32 = embeddings.astype(np.float32)
        self.index = faiss.IndexFlatL2(embeddings_f32.shape[1])
        self.index.add(embeddings_f32)

    def topk_indices(self, query: str, k: int = 10) -> list[int]:
        """
        Get the indices of the top k most similar documents for a query.

        Args:
            query: Search query string
            k: Number of top results to return (default: 10)

        Returns:
            List of document indices sorted by similarity (highest first)
        """
        if self.embedder is None:
            raise ValueError("OpenAIAPI is not initialized")

        embedded_query = self.embedder.embed(query)
        _, indices = self.index.search(np.array([embedded_query]), k)
        return indices[0].tolist()
