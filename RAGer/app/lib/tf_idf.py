"""
TF-IDF (Term Frequency-Inverse Document Frequency) search implementation.

This module provides functionality to:
1. Create a TF-IDF index from a list of documents
2. Search documents using TF-IDF scoring
3. Return ranked search results
4. Cache and load TF-IDF matrices for performance
"""

import pickle
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFSearch:
    """
    TF-IDF search engine for document collections.

    This class implements a complete TF-IDF search system that can:
    - Index documents using TF-IDF vectorization
    - Perform semantic search queries
    - Return ranked search results with relevance scores
    - Cache and load TF-IDF matrices for performance
    """

    def __init__(
        self,
        documents: List[str],
        max_features: int = 10000,
        cache_dir: Optional[str | Path] = None,
        use_cache: bool = True,
    ):
        """
        Initialize the TF-IDF search engine.

        Args:
            documents: List of document strings to index
            max_features: Maximum number of features (terms) to consider
            cache_dir: Directory to store cache files (default: app/data/cache)
            use_cache: Whether to use caching (default: True)
        """
        self.documents = documents
        self.max_features = max_features
        self.use_cache = use_cache

        # Set up cache directory
        if cache_dir is None:
            # Default to app/data/cache relative to this file
            current_dir = Path(__file__).parent
            self.cache_dir = current_dir.parent / "data" / "cache"
        else:
            self.cache_dir = Path(cache_dir)

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.vectorizer = None
        self.tfidf_matrix = None
        self.feature_names = None

        # Try to load from cache first, otherwise build index
        if self.use_cache and self._try_load_cache():
            print("Loaded TF-IDF index from cache")
        else:
            self._build_index()
            if self.use_cache:
                self._save_cache()

    def _build_index(self):
        """Build the TF-IDF index from the documents."""
        if not self.documents:
            raise ValueError("No documents provided for indexing")

        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words="english",  # Remove common English stop words
            lowercase=True,  # Convert to lowercase
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=2,  # Minimum document frequency
            max_df=0.95,  # Maximum document frequency (remove very common terms)
            strip_accents="unicode",
        )

        # Fit and transform the documents
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        self.feature_names = self.vectorizer.get_feature_names_out()

        print(
            f"Indexed {len(self.documents)} documents with {len(self.feature_names)} features"
        )

    def _generate_cache_key(self) -> str:
        """Generate a unique cache key based on documents and parameters."""
        # Create a hash of the documents content and parameters
        content_hash = hashlib.md5()

        # Hash document content
        for doc in self.documents:
            content_hash.update(doc.encode("utf-8"))

        # Hash parameters
        params = f"{self.max_features}"
        content_hash.update(params.encode("utf-8"))

        return content_hash.hexdigest()

    def _get_cache_file_path(self) -> Path:
        """Get the cache file path for the current configuration."""
        cache_key = self._generate_cache_key()
        return self.cache_dir / f"tfidf_cache_{cache_key}.pkl"

    def _save_cache(self):
        """Save the TF-IDF index to cache file."""
        try:
            cache_file = self._get_cache_file_path()

            cache_data = {
                "vectorizer": self.vectorizer,
                "tfidf_matrix": self.tfidf_matrix,
                "feature_names": self.feature_names,
                "max_features": self.max_features,
                "document_count": len(self.documents),
            }

            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            print(f"Saved TF-IDF index to cache: {cache_file}")

        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")

    def _try_load_cache(self) -> bool:
        """Try to load the TF-IDF index from cache file."""
        try:
            cache_file = self._get_cache_file_path()

            if not cache_file.exists():
                return False

            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            # Verify cache compatibility
            if (
                cache_data["document_count"] != len(self.documents)
                or cache_data["max_features"] != self.max_features
            ):
                print("Cache incompatible with current configuration, rebuilding index")
                return False

            # Load cached data
            self.vectorizer = cache_data["vectorizer"]
            self.tfidf_matrix = cache_data["tfidf_matrix"]
            self.feature_names = cache_data["feature_names"]

            return True

        except Exception as e:
            print(f"Warning: Failed to load cache: {e}")
            return False

    def clear_cache(self):
        """Clear all cache files for this search engine."""
        try:
            cache_file = self._get_cache_file_path()
            if cache_file.exists():
                cache_file.unlink()
                print(f"Cleared cache file: {cache_file}")
        except Exception as e:
            print(f"Warning: Failed to clear cache: {e}")

    def rebuild_index(self):
        """Force rebuild the TF-IDF index and update cache."""
        print("Rebuilding TF-IDF index...")
        self._build_index()
        if self.use_cache:
            self._save_cache()
        print("Index rebuild complete")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float, str]]:
        """
        Search for documents using TF-IDF scoring.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of tuples: (document_index, score, document_preview)
        """
        if not query.strip():
            return []

        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])

        # Calculate cosine similarity between query and all documents
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0:  # Only include relevant results
                # Create document preview (first 200 characters)
                doc_preview = (
                    self.documents[idx][:200] + "..."
                    if len(self.documents[idx]) > 200
                    else self.documents[idx]
                )
                results.append((idx, score, doc_preview))

        return results

    def search_with_filters(
        self, query: str, top_k: int = 10, min_score: float = 0.0
    ) -> List[Tuple[int, float, str]]:
        """
        Search with additional filtering options.

        Args:
            query: Search query string
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of tuples: (document_index, score, document_preview)
        """
        results = self.search(query, top_k)

        # Filter by minimum score
        filtered_results = [
            (idx, score, preview)
            for idx, score, preview in results
            if score >= min_score
        ]

        return filtered_results

    def get_document_terms(
        self, doc_index: int, top_terms: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get the top TF-IDF terms for a specific document.

        Args:
            doc_index: Index of the document
            top_terms: Number of top terms to return

        Returns:
            List of tuples: (term, tfidf_score)
        """
        if doc_index >= len(self.documents):
            raise ValueError(f"Document index {doc_index} out of range")

        # Get document vector
        doc_vector = self.tfidf_matrix[doc_index].toarray().flatten()

        # Get indices of top terms
        top_term_indices = np.argsort(doc_vector)[::-1][:top_terms]

        terms = []
        for idx in top_term_indices:
            if doc_vector[idx] > 0:
                terms.append((self.feature_names[idx], doc_vector[idx]))

        return terms

    def get_most_common_terms(self, top_terms: int = 20) -> List[Tuple[str, float]]:
        """
        Get the most common terms across all documents.

        Args:
            top_terms: Number of top terms to return

        Returns:
            List of tuples: (term, average_tfidf_score)
        """
        # Calculate average TF-IDF scores across all documents
        avg_scores = np.mean(self.tfidf_matrix.toarray(), axis=0)

        # Get top terms
        top_term_indices = np.argsort(avg_scores)[::-1][:top_terms]

        terms = []
        for idx in top_term_indices:
            if avg_scores[idx] > 0:
                terms.append((self.feature_names[idx], avg_scores[idx]))

        return terms

    def search_by_term(self, term: str) -> List[Tuple[int, float]]:
        """
        Find documents that contain a specific term.

        Args:
            term: Term to search for

        Returns:
            List of tuples: (document_index, tfidf_score)
        """
        if term not in self.feature_names:
            return []

        term_index = list(self.feature_names).index(term)
        term_scores = self.tfidf_matrix[:, term_index].toarray().flatten()

        # Get documents with non-zero scores for this term
        results = [(i, score) for i, score in enumerate(term_scores) if score > 0]

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)

        return results


def create_tfidf_search(
    documents: List[str],
    max_features: int = 10000,
    cache_dir: Optional[str | Path] = None,
    use_cache: bool = True,
) -> TFIDFSearch:
    """
    Convenience function to create a TF-IDF search engine.

    Args:
        documents: List of document strings
        max_features: Maximum number of features to consider
        cache_dir: Directory to store cache files
        use_cache: Whether to use caching

    Returns:
        Configured TFIDFSearch instance
    """
    return TFIDFSearch(documents, max_features, cache_dir, use_cache)


def create_cached_tfidf_search(
    documents: List[str],
    max_features: int = 10000,
    cache_dir: Optional[str | Path] = None,
) -> TFIDFSearch:
    """
    Convenience function to create a cached TF-IDF search engine.

    Args:
        documents: List of document strings
        max_features: Maximum number of features to consider
        cache_dir: Directory to store cache files

    Returns:
        Configured TFIDFSearch instance with caching enabled
    """
    return TFIDFSearch(documents, max_features, cache_dir, use_cache=True)


def simple_search(
    documents: List[str], query: str, top_k: int = 5, use_cache: bool = True
) -> List[Tuple[int, float, str]]:
    """
    Simple one-shot search function with optional caching.

    Args:
        documents: List of document strings
        query: Search query
        top_k: Number of results to return
        use_cache: Whether to use caching

    Returns:
        List of search results
    """
    search_engine = create_tfidf_search(documents, use_cache=use_cache)
    return search_engine.search(query, top_k)


# Example usage and testing
if __name__ == "__main__":
    # Example documents
    sample_docs = [
        "The quick brown fox jumps over the lazy dog. This is a sample document about animals.",
        "Machine learning is a subset of artificial intelligence. It involves training models on data.",
        "Python is a popular programming language for data science and machine learning applications.",
        "Natural language processing helps computers understand human language and text.",
        "Data science combines statistics, programming, and domain expertise to extract insights.",
    ]

    # Create search engine with caching
    search_engine = create_cached_tfidf_search(sample_docs)

    # Perform searches
    print("Searching for 'machine learning':")
    results = search_engine.search("machine learning", top_k=3)
    for idx, score, preview in results:
        print(f"Doc {idx}: Score {score:.3f} - {preview}")

    print("\nSearching for 'animals':")
    results = search_engine.search("animals", top_k=3)
    for idx, score, preview in results:
        print(f"Doc {idx}: Score {score:.3f} - {preview}")

    print("\nMost common terms:")
    common_terms = search_engine.get_most_common_terms(top_terms=10)
    for term, score in common_terms:
        print(f"{term}: {score:.3f}")

    # Test cache functionality
    print("\nTesting cache functionality...")
    print("Creating new search engine (should load from cache):")
    search_engine2 = create_cached_tfidf_search(sample_docs)

    # Clear cache
    search_engine.clear_cache()
    print("Cache cleared. Creating new search engine (should rebuild index):")
    search_engine3 = create_cached_tfidf_search(sample_docs)
