from pathlib import Path
import polars as pl
from app.src.search.bm25 import BM25
from app.src.util.read_documents import read_text_documents
from app.src.api.api_objects import SearchType


class Search:
    def __init__(self, df: pl.DataFrame):
        self.df = df
        # Add the chunk annotations to the chunks so that they are included in searches.
        annotated_corpus = df.select(
            pl.concat_str(
                [pl.col("annotations"), pl.col("chunk_text")],
                separator="\n\n"
            ).alias("annotated_chunk")
        ).to_series().to_list()
        self.corpus = tuple(annotated_corpus)
        self.bm25 = BM25(self.corpus)

    def search(self, text: str, search_type: SearchType, k: int = 10) -> list[dict[str, str]]:
        if search_type == SearchType.BM25:
            return self.bm25_search(text, k)
        elif search_type == SearchType.VECTOR_SEARCH:
            return self.vector_search.search(text, k)
        elif search_type == SearchType.RANK_FUSION:
            return self.rank_fusion.search(text, k)
        else:
            raise ValueError(f"Invalid search type: {search_type}")

    def bm25_search(self, text: str, k: int = 10) -> list[dict[str, str]]:
        bm25_indices = self.bm25.topk_indices(text, k)
        return self.df.filter(pl.col("idx").is_in(bm25_indices))[["file_path", "chunk_text"]].to_dicts()

    def vector_search(self, text: str, k: int = 10) -> list[dict[str, str]]:
        # TODO: Implement vector search
        raise NotImplementedError("Vector search is not implemented yet")

    def rank_fusion(self, text: str, k: int = 10) -> list[dict[str, str]]:
        # TODO: Implement rank fusion
        
        # Multithread bm25 search and vector search
        # Rank fusion the results
        # Rerank the results
        # Return top k results

        raise NotImplementedError("Rank fusion is not implemented yet")
