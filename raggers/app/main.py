#!/usr/bin/env python3
"""
Main entry point for the ADLM 2025 Data Challenge RAG Application.
"""

import sys
from pathlib import Path


def main():
    """Main entry point for the RAG application."""
    print("ADLM 2025 Data Challenge RAG Application")
    print("=" * 50)

    # Look for extracted documents in app/data/extracted_docs
    data_dir = Path(__file__).parent / "data"
    extracted_docs_dir = data_dir / "extracted_docs"

    if not extracted_docs_dir.exists():
        print("No extracted documents found.")
        print("Please run 'poetry run extract-pdfs' first to extract PDF content.")
        sys.exit(1)

    # Count extracted documents
    txt_files = list(extracted_docs_dir.rglob("*.txt"))
    print(f"Found {len(txt_files)} extracted text documents.")

    # TODO: Implement RAG functionality here
    print("\nRAG functionality coming soon...")
    print("This will include:")
    print("- Document embedding and vectorization")
    print("- Query processing and retrieval")
    print("- Response generation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
