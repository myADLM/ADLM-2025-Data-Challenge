"""
BM25 (Best Matching 25) implementation for document search and retrieval.

This module provides a BM25-based search functionality that can be used to find
the most relevant documents in a corpus based on a query. The implementation
includes NLTK-based text tokenization.
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from itertools import chain

import fastbm25
import nltk
import polars as pl

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
        self.token_to_code = {}
        encoded_corpus = []

        t0 = time.perf_counter()
        self.corpus_size = len(corpus)

        # Pre-tokenize all documents using parallel processing
        # Use more workers for larger corpora, but cap at CPU count
        # Parallelization improves data prep time by 6x
        max_workers = min(8, max(4, len(corpus) // 500), os.cpu_count())
        print(f"Tokenizing {len(corpus)} documents using {max_workers} workers...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            all_tokenized_docs = list(executor.map(BM25.tokenize, corpus))

        # Collect all unique tokens efficiently using set union
        print("Building vocabulary from tokens...")
        all_tokens = set(chain.from_iterable(all_tokenized_docs))

        # Build token-to-code mapping once (use dict.get for O(1) lookup)
        print("Building vocabulary...")
        self.token_to_code = {
            token: idx for idx, token in enumerate(sorted(all_tokens))
        }

        # Encode all documents using list comprehension and pre-built mapping
        print("Encoding documents...")
        encoded_corpus = [
            [self.token_to_code[token] for token in tokens]
            for tokens in all_tokenized_docs
        ]
        print("Data prepped in {}s".format(time.perf_counter() - t0))

        t0 = time.perf_counter()
        self.fast_bm25 = fastbm25.BM25(encoded_corpus)
        print("Rust BM25 index created in {}s".format(time.perf_counter() - t0))

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
            [self.encode_token(token) for token in BM25.tokenize(query)], k
        )

    def encode_token(self, token: str) -> int:
        return self.token_to_code.get(token, self.corpus_size)

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
