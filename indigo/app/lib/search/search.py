from pathlib import Path
from app.lib.search.tf_idf import create_cached_tfidf_search, create_tfidf_search
from app.lib.util.read_text_documents import read_text_documents


class Search:
    def __init__(
        self,
        document_path: str | Path,
        cache_path: str | Path = None,
        use_cache: bool = True,
    ):
        """
        Initialize the Search class with document indexing and caching.

        Args:
            document_path: Path to directory containing text documents
            cache_path: Path to directory for TF-IDF cache (default: app/dbs/tf_idf)
            use_cache: Whether to use TF-IDF caching (default: True)
        """
        document_tuples = read_text_documents(document_path)

        # Extract document paths and content separately
        self.document_paths = [path for path, _ in document_tuples]
        self.document_contents = [content for _, content in document_tuples]

        # Set default cache path if not provided
        if cache_path is None:
            current_dir = Path(__file__).parent
            cache_path = current_dir.parent / "dbs" / "tf_idf"

        # Create cache directory if it doesn't exist
        Path(cache_path).mkdir(parents=True, exist_ok=True)

        # Pass document contents to TF-IDF search engine
        self.tfidf_search = (
            create_cached_tfidf_search(self.document_contents, cache_dir=cache_path)
            if use_cache
            else create_tfidf_search(self.document_contents, cache_dir=cache_path)
        )

    def add_path_context(self, document_tuples: list[tuple[str, str]]) -> list[str]:
        """
        Add path context to document contents.
        """
        return [
            f"File: {' '.join(path.parts)}\n\n{content}"
            for path, content in document_tuples
        ]

    def search(self, query: str, top_k: int = 10):
        """Search for documents using the query."""
        return self.tfidf_search.search(query, top_k)

    def search_with_paths(self, query: str, top_k: int = 10):
        """
        Search for documents and return results with file paths.

        Returns:
            List of tuples: (document_path, score, document_preview)
        """
        results = self.tfidf_search.search(query, top_k)

        # Map document indices to paths and add previews
        enhanced_results = []
        for doc_idx, score, _ in results:
            doc_path = self.document_paths[doc_idx]
            doc_content = self.document_contents[doc_idx]
            # Create preview (first 200 characters)
            preview = (
                doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
            )
            enhanced_results.append((doc_path, score, preview))

        return enhanced_results

    def get_document_path(self, doc_index: int) -> str:
        """Get the file path for a document index."""
        if 0 <= doc_index < len(self.document_paths):
            return self.document_paths[doc_index]
        raise ValueError(f"Document index {doc_index} out of range")

    def get_document_content(self, doc_index: int) -> str:
        """Get the content for a document index."""
        if 0 <= doc_index < len(self.document_contents):
            return self.document_contents[doc_index]
        raise ValueError(f"Document index {doc_index} out of range")

    def clear_cache(self):
        """Clear the TF-IDF cache."""
        self.tfidf_search.clear_cache()

    def rebuild_index(self):
        """Force rebuild the TF-IDF index."""
        self.tfidf_search.rebuild_index()

    def tf_idf_most_common_terms(self, top_terms: int = 20):
        """
        Get the most common terms across all documents in the TF-IDF index.

        Args:
            top_terms: Number of top terms to return

        Returns:
            List of tuples: (term, average_tfidf_score)
        """
        return self.tfidf_search.get_most_common_terms(top_terms)
