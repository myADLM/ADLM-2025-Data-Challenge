import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import polars as pl

from app.src.api.api_objects import SearchType
from app.src.search.bm25 import BM25
from app.src.search.vector_search import VectorSearch
from app.src.util.read_documents import read_text_documents


class Search:
    def __init__(self, df: pl.DataFrame):
        self.df = df
        # Add the chunk annotations to the chunks so that they are included in searches.
        self.corpus = df["contextual_chunk"].to_list()
        self.corpus_size = len(self.corpus)
        self.bm25 = BM25(self.corpus)
        self.vector_search = VectorSearch(self.df["embedding"])

    def search(
        self, text: str, search_type: SearchType, k: int = 10
    ) -> list[dict[str, list[str]]]:
        if search_type == SearchType.BM25:
            return self.bm25_search(text, k)
        elif search_type == SearchType.VECTOR_SEARCH:
            return self.vector_search.search(text, k)
        elif search_type == SearchType.RANK_FUSION:
            return self.rank_fusion.search(text, k)
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
        indices = self.vector_search.topk_indices(text, k)
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
        print("Performing rank fusion...")

        def get_bm25_ranks():
            """Get BM25 rankings in a separate thread."""
            indices = self.bm25.topk_indices(text, 120)
            return {idx: r for r, idx in enumerate(indices)}

        def get_vector_ranks():
            """Get vector search rankings in a separate thread."""
            indices = self.vector_search.topk_indices(text, 120)
            return {idx: r for r, idx in enumerate(indices)}

        max_workers = min((os.cpu_count() or 1), 8)

        t0 = time.perf_counter()
        # TODO: compare times for different parallelization strategies
        
        # Use ThreadPoolExecutor to calculate both rankings in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit both tasks
            bm25_future = executor.submit(get_bm25_ranks)
            vector_future = executor.submit(get_vector_ranks)

            # Get results
            a_ranks = bm25_future.result()
            b_ranks = vector_future.result()

        print(f"Ranks calculated in {time.perf_counter() - t0} seconds")

        t0 = time.perf_counter()
        # Combine all unique indices from both rankings
        ranks = list(set([i for i in a_ranks.keys()] + [i for i in b_ranks.keys()]))

        # Apply reciprocal rank fusion formula: 1/(60 + rank_a) + 1/(60 + rank_b)
        # Use get() with default value 120 for indices not in either ranking
        def fusion_score(idx):
            rank_a = a_ranks.get(idx, 120)
            rank_b = b_ranks.get(idx, 120)
            return (1.0 / (60.0 + rank_a)) + (1.0 / (60.0 + rank_b))

        # Sort by fusion score and return top k
        sorted_ranks = sorted(ranks, key=fusion_score, reverse=True)[:k]

        # Convert indices back to records
        records = {
            record["idx"]: record
            for record in self.df.filter(pl.col("idx").is_in(sorted_ranks)).to_dicts()
        }

        print(f"Ranks fused in {time.perf_counter() - t0} seconds")

        return [records[idx] for idx in sorted_ranks]

    def rerank(self, text: str, results: list[int]) -> list[int]:
        # TODO: implement reranking
        pass
