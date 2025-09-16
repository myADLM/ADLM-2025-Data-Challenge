from pathlib import Path
import polars as pl
from app.src.search.bm25 import BM25
from app.src.util.read_documents import read_text_documents


class Search:
    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.corpus = list(df["chunk_text"])
        self.bm25 = BM25(self.corpus)

    def search(self, text: str, k: int = 10) -> list[int]:
        bm25_indices = self.bm25.topk_indices(text, k)

        # TODO: Add vector search
        # TODO: Add rank fusion
        # TODO: Add reranking
        
        return self.df.filter(pl.col("idx").is_in(bm25_indices))["file_path"].to_list()
