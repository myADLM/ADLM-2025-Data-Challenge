import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Protocol, Type
from app.src.util.open_ai_api import OpenAIAPI

import faiss
import numpy as np
import polars as pl
import requests


class VectorSearch:
    def __init__(self, embeddings: pl.Series, embedder: OpenAIAPI):
        self.embedder = embedder
        embeddings = np.vstack(embeddings)
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
        embedded_query = self.embedder.embed(query)
        _, indices = self.index.search(np.array([embedded_query]), k)
        return indices[0].tolist()
    
