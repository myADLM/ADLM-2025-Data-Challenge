"""
BM25 (Best Matching 25) implementation for document search and retrieval.

This module provides a BM25-based search functionality that can be used to find
the most relevant documents in a corpus based on a query. The implementation
includes NLTK-based text tokenization.
"""

import logging
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor

import fastbm25

logger = logging.getLogger("app")

_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _tokenize_batch(docs: list[str]) -> list[list[str]]:
    return [_TOKEN_RE.findall(doc.lower()) for doc in docs]


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
        logger.info("Initializing BM25")

        self.token_to_code: dict[str, int] = {}
        self.corpus_size = len(corpus)
        self._oov_id = 0
        t0 = time.perf_counter()

        # Pre-tokenize all documents using parallel processing
        # Use more workers for larger corpora, but cap at CPU count
        # Parallelization improves data prep time by 6x
        max_workers = min(8, os.cpu_count() or 1)
        encoded_corpus: list[list[int]] = []
        next_id = 0

        batch_size = 1000
        # Chunk the corpus
        batches = [
            corpus[i : i + batch_size] for i in range(0, len(corpus), batch_size)
        ]

        logger.info("Tokenizing corpus")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for tokenized_batch in executor.map(_tokenize_batch, batches, chunksize=1):
                for tokens in tokenized_batch:
                    enc = []
                    for token in tokens:
                        code = self.token_to_code.get(token)
                        if code is None:
                            code = next_id
                            self.token_to_code[token] = code
                            next_id += 1
                        enc.append(code)
                    encoded_corpus.append(enc)

        self._oov_id = next_id

        logger.info("Creating Rust BM25 index")
        self.fast_bm25 = fastbm25.BM25(encoded_corpus)
        logger.info("Rust BM25 index created in {}s".format(time.perf_counter() - t0))

    def topk_indices(self, query: str, k: int = 10) -> list[int]:
        """
        Get the indices of the top k most relevant documents for a query.

        Args:
            query: Search query string
            k: Number of top results to return (default: 10)

        Returns:
            List of document indices sorted by relevance (highest first)
        """
        return self.fast_bm25.get_top_k_indices(
            [self.encode_token(token) for token in tokenize(query)], k
        )

    def encode_token(self, token: str) -> int:
        return self.token_to_code.get(token, self._oov_id)
