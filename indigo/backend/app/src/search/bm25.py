"""
BM25 (Best Matching 25) implementation for document search and retrieval.

This module provides a BM25-based search functionality that can be used to find
the most relevant documents in a corpus based on a query. The implementation
includes NLTK-based text tokenization.
"""

from rank_bm25 import BM25Okapi
import nltk
import numpy as np
import time

# Download required NLTK data for tokenization
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import word_tokenize


class BM25:
    """
    BM25 search implementation with S3 model persistence.

    This class provides BM25-based document search functionality. It uses NLTK for text
    tokenization and provides methods for both document retrieval and index-based search.
    """

    def __init__(self, corpus: list[str]):
        """
        Initialize BM25 search with a corpus of documents.

        Args:
            corpus: List of documents to search through
        """
        self.corpus = list(corpus)
        t0 = time.perf_counter()
        self.bm25 = BM25Okapi(corpus=corpus, tokenizer=BM25.tokenize)
        print(f"Built BM25 index in {time.perf_counter()-t0}s")

    def topk_indices(self, query: str, k: int = 10) -> list[int]:
        """
        Get the indices of the top k most relevant documents for a query.

        Args:
            query: Search query string
            k: Number of top results to return (default: 10)

        Returns:
            List of document indices sorted by relevance (highest first)
        """
        t0 = time.perf_counter()
        doc_scores = np.asarray(self.bm25.get_scores(BM25.tokenize(query)))
        idx = np.argpartition(doc_scores, -k)[-k:]
        result = list(idx[np.argsort(doc_scores[idx])][::-1])
        print(f"BM25 search took {time.perf_counter()-t0}s")
        return result

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """
        Tokenize text using NLTK's word tokenizer.

        Args:
            text: Input text to tokenize

        Returns:
            List of lowercase tokens
        """
        return word_tokenize(text.lower())
