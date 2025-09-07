#!/usr/bin/env python3
"""
PDF extraction script for the ADLM 2025 Data Challenge RAG Application.
"""

import sys
import argparse
import shutil
from app.lib.util.download_data import download_labdocs
from app.lib.database.build_database import build_database
from pathlib import Path


def main():
    """Main entry point to build all requirements for the project."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF documents for the ADLM 2025 Data Challenge RAG Application",
        epilog="""Examples:
            poetry run build                           # Use default LabDocs directory
            poetry run build --doc-path /path/to/docs  # Use custom documents directory
            poetry run build --output-data-dir /path/to/output  # Use custom output directory
            poetry run build --force-download          # Force download of LabDocs
        """,
    )
    parser.add_argument(
        "--doc-path",
        type=str,
        metavar="PATH",
        default="app/input_data",
        help="Custom path to the documents directory containing PDF files (default: app/input_data)",
    )
    parser.add_argument(
        "--database-dir",
        type=str,
        metavar="PATH",
        default="app/database",
        help="Output directory for extracted text files (default: app/database)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force download and extraction of LabDocs from Zenodo",
    )

    args = parser.parse_args()
    doc_path = Path(args.doc_path)

    # Handle force download option
    if args.force_download:
        print("Force downloading LabDocs...")

        # Remove all contents from doc_path directory if it exists
        if doc_path.exists():
            print(f"Clearing existing contents from '{doc_path}'...")
            try:
                # Remove all contents but keep the directory
                for item in doc_path.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                print(f"Successfully cleared contents from '{doc_path}'")
            except Exception as e:
                print(f"Warning: Error clearing directory '{doc_path}': {e}")
        else:
            # Create the directory if it doesn't exist
            doc_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory '{doc_path}'")

        # Download to the specified doc-path directory
        if download_labdocs(output_dir=doc_path):
            print("LabDocs download completed successfully.")
        else:
            print("Failed to download LabDocs.")
            sys.exit(1)
        return

    # Check if doc-path directory exists and is not empty
    if not doc_path.exists():
        print(f"Document directory '{doc_path}' does not exist.")
        print("Downloading LabDocs...")
        if download_labdocs(output_dir=doc_path):
            print("LabDocs download completed successfully.")
        else:
            print("Failed to download LabDocs.")
            sys.exit(1)
    elif not any(doc_path.iterdir()):
        print(f"Document directory '{doc_path}' is empty.")
        print("Downloading LabDocs...")
        if download_labdocs(output_dir=doc_path):
            print("LabDocs download completed successfully.")
        else:
            print("Failed to download LabDocs.")
            sys.exit(1)
    else:
        print(f"Using existing document directory: {doc_path}")

    database_path = Path(args.database_dir)
    build_database(input_docs_path=doc_path, database_path=database_path)


if __name__ == "__main__":
    main()
