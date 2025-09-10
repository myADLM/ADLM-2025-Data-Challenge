#!/usr/bin/env python3
"""
PDF extraction script for the ADLM 2025 Data Challenge RAG Application.
"""

import sys
import argparse
import shutil
from app.src.util.download_data import download_labdocs_zip
from app.src.database.build_database import build_database
from pathlib import Path


def main():
    """Main entry point to build all requirements for the project."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF documents for the ADLM 2025 Data Challenge RAG Application",
        epilog="""Examples:
            poetry run build                           # Use default LabDocs directory
            poetry run build --zip-path /path/to/zip   # Use custom documents directory
            poetry run build --output-data-dir /path/to/output  # Use custom output directory
            poetry run build --force-download          # Force download of LabDocs
        """,
    )
    parser.add_argument(
        "--zip-path",
        type=str,
        metavar="PATH",
        default="app/input_data/raw_input_data.zip",
        help="Custom path to the zip file containing PDF files (default: app/input_data/raw_input_data.zip)",
    )
    parser.add_argument(
        "--database-dir",
        type=str,
        metavar="PATH",
        default="app/database",
        help="Output directory for extracted text files (default: app/database)",
    )
    parser.add_argument("--clean", action="store_true", help="Run build from scratch")

    args = parser.parse_args()
    zip_path = Path(args.zip_path)
    database_path = Path(args.database_dir)

    # Handle force download option
    if args.clean:
        print("Cleaning database...")
        if zip_path.exists():
            print(f"Clearing existing contents from '{zip_path}'...")
            zip_path.unlink()
            print(f"Successfully cleared contents from '{zip_path}'")
        else:
            print(f"Zip file '{zip_path}' does not exist.")
        if database_path.exists():
            print(f"Clearing existing contents from '{database_path}'...")
            shutil.rmtree(database_path)
            print(f"Successfully cleared contents from '{database_path}'")
        else:
            print(f"Database directory '{database_path}' does not exist.")

    # Check if zip file exists
    if not zip_path.exists():
        print(f"Document directory '{zip_path}' does not exist.")
        print("Downloading LabDocs...")
        if download_labdocs_zip(output_path=zip_path):
            print("LabDocs download completed successfully.")
        else:
            print("Failed to download LabDocs.")
            sys.exit(1)
    else:
        print(f"Using existing document directory: {zip_path}")

    database_path = Path(args.database_dir)
    build_database(
        input_zip_path=zip_path, database_path=database_path, force_rebuild=args.clean
    )


if __name__ == "__main__":
    main()
