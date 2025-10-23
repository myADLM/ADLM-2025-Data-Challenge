import logging
import time

import numpy as np
import polars as pl
from numpy.typing import NDArray

from app.src.api.api_objects import SearchType
from app.src.search.bm25 import BM25
from app.src.search.vector_search import VectorSearch


class Search:
    def __init__(self, chunk_df: pl.DataFrame, embeddings: NDArray[np.float32]):
        self.df = chunk_df
        # Store corpus as a lazy series to avoid loading all text into memory at once
        self.corpus_series = chunk_df["contextual_chunk"]
        self.corpus_size = len(self.corpus_series)
        self.vector_db = VectorSearch(embeddings)
        # Initialize BM25 with lazy corpus loading
        self.bm25 = BM25(self.corpus_series.to_list())

    def search(
        self, text: str, search_type: SearchType, k: int = 10
    ) -> list[dict[str, str]]:
        if search_type == SearchType.BM25:
            return self.bm25_search(text, k)
        elif search_type == SearchType.VECTOR_SEARCH:
            return self.vector_search(text, k)
        elif search_type == SearchType.RANK_FUSION:
            return self.rank_fusion(text, k)
        else:
            raise ValueError(f"Invalid search type: {search_type}")

    def bm25_search(self, text: str, k: int = 10) -> list[dict[str, str]]:
        indices = self.bm25.topk_indices(text, k)
        records = {
            record["idx"]: record
            for record in self.df.filter(pl.col("idx").is_in(indices)).to_dicts()
        }

        # sort the records by the BM25 score
        return [records[idx] for idx in indices]

    def vector_search(self, text: str, k: int = 10) -> list[dict[str, str]]:
        indices = self.vector_db.topk_indices(text, k)
        records = {
            record["idx"]: record
            for record in self.df.filter(pl.col("idx").is_in(indices)).to_dicts()
        }
        return [records[idx] for idx in indices]

    def rank_fusion(self, text: str, k: int = 10) -> list[dict[str, str]]:
        """
        Perform rank fusion by combining BM25 and vector search results using multithreaded computation.

        Args:
            text: Search query string
            k: Number of top results to return

        Returns:
            List of top k results ranked by fusion score
        """
        logger = logging.getLogger("app")
        logger.info(
            f"Ranking fusion search for query: {text} (method called at {time.time()})"
        )

        def get_bm25_ranks():
            """Get BM25 rankings in a separate thread."""
            indices = self.bm25.topk_indices(text, 120)
            return {idx: r for r, idx in enumerate(indices)}

        def get_vector_ranks():
            """Get vector search rankings in a separate thread."""
            indices = self.vector_db.topk_indices(text, 120)
            return {idx: r for r, idx in enumerate(indices)}

        logger = logging.getLogger("app")
        t0 = time.perf_counter()
        a_ranks = get_bm25_ranks()
        logger.debug(f"BM25: {time.perf_counter()-t0}")
        t0 = time.perf_counter()
        b_ranks = get_vector_ranks()
        logger.debug(f"Vector: {time.perf_counter()-t0}")

        t0 = time.perf_counter()
        # Combine all unique indices from both rankings
        idxs = list(set([i for i in a_ranks.keys()] + [i for i in b_ranks.keys()]))

        # Apply reciprocal rank fusion formula: 1/(60 + rank_a) + 1/(60 + rank_b)
        # Use get() with default value 121 for indices not in either ranking
        def fusion_score(idx):
            rank_a = a_ranks.get(idx, 121)
            rank_b = b_ranks.get(idx, 121)
            return (1.0 / (60.0 + rank_a)) + (1.0 / (60.0 + rank_b))

        # Sort by fusion score and return top k
        sorted_ranks = sorted(idxs, key=fusion_score, reverse=True)[:k]

        # Convert indices back to records
        records = {
            record["idx"]: record
            for record in self.df.filter(pl.col("idx").is_in(sorted_ranks)).to_dicts()
        }
        logger.debug(f"Rank fusion: {time.perf_counter()-t0}")

        return [records[idx] for idx in sorted_ranks]

    def rerank(self, text: str, results: list[int]) -> list[int]:
        # TODO: implement reranking
        pass
