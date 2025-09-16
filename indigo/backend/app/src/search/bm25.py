"""
BM25 (Best Matching 25) implementation for document search and retrieval.

This module provides a BM25-based search functionality that can be used to find
the most relevant documents in a corpus based on a query. The implementation
includes S3 integration for model persistence and NLTK-based text tokenization.
"""

from rank_bm25 import BM25Okapi
from botocore.exceptions import ClientError
from app.src.util.s3 import download_file_from_s3, get_s3_client
import nltk
import pickle
import io
import numpy as np
import time

# Download required NLTK data for tokenization
nltk.download('punkt', quiet=True)
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import word_tokenize


class BM25:
    """
    BM25 search implementation with S3 model persistence.
    
    This class provides BM25-based document search functionality with the ability
    to save and load trained models from S3. It uses NLTK for text tokenization
    and provides methods for both document retrieval and index-based search.
    """

    def __init__(self, corpus: list[str], s3_bucket: str = "adlm-data-challenge", s3_key: str = "bm25.pkl", overwrite: bool = False):
        """
        Initialize BM25 search with a corpus of documents.
        
        Args:
            corpus: List of documents to search through
            s3_bucket: S3 bucket name for model persistence (default: "adlm-data-challenge")
            s3_key: S3 key for the saved model file (default: "bm25.pkl")
            overwrite: If True, force retrain the model even if one exists in S3
        """
        self.corpus = list(corpus)
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.bm25 = self._make_bm25(corpus, overwrite)

    def search(self, query: str, k: int = 10) -> list[tuple[str, int]]:
        """
        Search for the most relevant documents in the corpus.
        
        Args:
            query: Search query string
            k: Number of top results to return (default: 10)
            
        Returns:
            List of tuples containing (document_text, document_index) for the top k results
        """
        topk_indices = self.topk_indices(query, k)
        return [(self.corpus[i], i) for i in topk_indices]

    def topk_indices(self, query: str, k: int = 10) -> list[int]:
        """
        Get the indices of the top k most relevant documents for a query.
        
        Args:
            query: Search query string
            k: Number of top results to return (default: 10)
            
        Returns:
            List of document indices sorted by relevance (highest first)
        """
        doc_scores = np.asarray(self.bm25.get_scores(BM25.tokenize(query)))
        idx = np.argpartition(doc_scores, -k)[-k:]
        return list(idx[np.argsort(doc_scores[idx])][::-1])

    def _make_bm25(self, corpus: list[str], overwrite: bool = False):
        """
        Create or load a BM25 model from S3 or create a new one.
        
        Args:
            corpus: List of documents to train the model on
            overwrite: If True, force retrain even if model exists in S3
            
        Returns:
            Trained BM25Okapi model instance
        """
        if overwrite:
            # Force retrain the model
            self.bm25 = BM25Okapi(corpus=corpus, tokenizer=BM25.tokenize)
            self._save_bm25()
            return self.bm25
        
        try:
            # Try to load existing model from S3
            t0 = time.time()
            data = download_file_from_s3(self.s3_bucket, self.s3_key)
            t1 = time.time()
            with io.BytesIO(data) as buf:
                buf.seek(0)
                self.bm25 = pickle.load(buf)
            print(f"S3 get: {t1-t0}s    unpickle: {time.time()-t1}s")
            print("BM25 Constructed from file")
        except FileNotFoundError:
            # Model doesn't exist in S3, create and save a new one
            print("BM25 not found in S3, creating new one")
            self.bm25 = BM25Okapi(corpus=corpus, tokenizer=BM25.tokenize)
            self._save_bm25()
        return self.bm25

    def _save_bm25(self):
        """
        Save the trained BM25 model to S3 for future use. No not serialize the idf. This saves a lot of time.
        
        The model is serialized using pickle and uploaded
        to the configured S3 bucket and key.
        """
        print("Saving BM25 to S3")
        # TODO: Make this fast. Loading takes a long time. This is because self.bm25.idf is a large dictionary.
        #       We could put the idf in a separate file and load in parallel.
        with io.BytesIO() as buf:
            pickle.dump(self.bm25, buf)
            buf.seek(0)
            get_s3_client().upload_fileobj(buf, self.s3_bucket, self.s3_key, ExtraArgs={"ContentType": "application/octet-stream"})
        
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