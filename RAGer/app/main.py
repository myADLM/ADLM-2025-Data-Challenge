#!/usr/bin/env python3
"""
Main entry point for the ADLM 2025 Data Challenge RAG Application.
"""

import sys
from pathlib import Path
from app.lib.search import Search


def display_results(results, query):
    """Display search results in a formatted way."""
    if results:
        print(f"\nFound {len(results)} relevant documents for: '{query}'")
        print("-" * 80)
        for i, (doc_path, score, preview) in enumerate(results, 1):
            print(f"\n{i}. File: {doc_path}")
            print(f"   Score: {score:.3f}")
            print(f"   Preview: {preview}")
            print("-" * 40)
    else:
        print(f"\nNo relevant documents found for: '{query}'")


def main():
    """Main entry point for the RAG application."""
    print("ADLM 2025 Data Challenge RAG Application")
    print("=" * 50)

    # Look for extracted documents in app/data/extracted_docs
    data_dir = Path(__file__).parent / "data"
    extracted_docs_dir = data_dir / "extracted_docs"

    if not extracted_docs_dir.exists():
        print("No extracted documents found.")
        print("Please run 'poetry run build' first to extract PDF content.")
        sys.exit(1)

    # Count extracted documents
    txt_files = list(extracted_docs_dir.rglob("*.txt"))
    print(f"Found {len(txt_files)} extracted text documents.")

    # Initialize search engine
    print("Initializing search engine...")
    search = Search(extracted_docs_dir)
    print("Search engine ready!\n")

    # CLI interface
    print("Enter your search queries below. Type 'quit' to exit.")
    print("Type 'help' for available commands.\n")

    while True:
        try:
            query = input("Query: ").strip()

            if not query:
                continue

            if query.lower() == "quit":
                print("Goodbye!")
                break

            if query.lower() == "help":
                print("\nAvailable commands:")
                print("  - Enter any search query to search documents")
                print("  - 'quit' - Exit the application")
                print("  - 'help' - Show this help message")
                print("  - 'clear' - Clear the screen")
                print("  - 'count' - Show document count")
                print(
                    "  - 'most_common_terms' - Show the most common terms in the TF-IDF index"
                )
                print()
                continue

            if query.lower() == "clear":
                print("\n" * 50)  # Simple clear by printing many newlines
                continue

            if query.lower() == "count":
                print(f"\nTotal documents: {len(txt_files)}")
                print()
                continue

            if query.lower() == "most_common_terms":
                most_common_terms = search.tf_idf_most_common_terms()
                print(f"\nMost common terms in the TF-IDF index:")
                for term, count in most_common_terms:
                    print(f"  - {term}: {count}")
                print()
                continue

            # Perform search
            print(f"\nSearching for: '{query}'...")
            results = search.search_with_paths(query, top_k=10)

            # Display results
            display_results(results, query)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("Please try again.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
