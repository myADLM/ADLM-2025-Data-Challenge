from app.lib.database.extract_labdocs import extract_docs
from app.lib.database.chunker import chunk_docs
from pathlib import Path


def build_database(input_docs_path: Path, database_path: Path):
    """Build the database."""
    extract_docs(input_docs_path, database_path)
    extracted_docs_path = database_path / "extracted_docs"
    chunk_docs_path = database_path / "chunked_docs"
    chunk_docs(extracted_docs_path, chunk_docs_path)
    # Query LLM to add context to the chunks
    # Add file path context to the chunks
    # Build the vector database
    # Build the BM25 database
    # Done!
