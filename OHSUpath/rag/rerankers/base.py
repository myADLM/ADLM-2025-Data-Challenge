# rag/rerankers/base.py

from __future__ import annotations
from typing import Protocol, List, Tuple, Callable, Optional

class Reranker(Protocol):
    """
    Re-rank sparse candidates and return a list of (id, new_score) pairs.
    Higher scores are better.
    """

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[str, float]],   # [(chunk_id, bm25_score)]
        id2text: Callable[[str], str],         # chunk_id -> text
    ) -> List[Tuple[str, float]]: ...
