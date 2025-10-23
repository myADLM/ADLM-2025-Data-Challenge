import logging
import time

import faiss
import numpy as np
from numpy.typing import NDArray

from app.src.util.open_ai_api import EmbeddingsAPI


class VectorSearch:
    def __init__(self, embeddings: NDArray[np.float32]):
        logger = logging.getLogger("app")
        logger.info("Initializing VectorSearch")
        # Soft failure for EmbeddingsAPI
        try:
            self.embedder = EmbeddingsAPI()
        except Exception as e:
            logger.error(f"Error initializing EmbeddingsAPI: {e}")
            self.embedder = None

        logger.info(f"Embeddings shape: {embeddings.shape}")
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

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
            raise ValueError("EmbeddingsAPI is not initialized")

        logger = logging.getLogger("app")

        t0 = time.perf_counter()
        embedded_query = self.embedder.embed(query)
        logger.info(f"Time to embed query: {time.perf_counter()-t0}")
        t0 = time.perf_counter()
        _, indices = self.index.search(np.array([embedded_query]), k)
        logger.info(f"Time to search: {time.perf_counter()-t0}")
        return indices[0].tolist()
