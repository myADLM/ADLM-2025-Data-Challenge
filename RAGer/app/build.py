#!/usr/bin/env python3
"""
PDF extraction script for the ADLM 2025 Data Challenge RAG Application.
"""

import sys
import argparse
from app.lib.data_source import download_labdocs
from app.lib.extract_labdocs import extract_labdocs
from pathlib import Path


def main():
    """Main entry point to build all requirements for the project."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF documents for the ADLM 2025 Data Challenge RAG Application",
        epilog="""Examples:
            poetry run build                           # Use default LabDocs directory
            poetry run build --doc-path /path/to/docs  # Use custom documents directory
            poetry run build --force-download          # Force download of LabDocs
        """,
    )
    parser.add_argument(
        "--doc-path",
        type=str,
        metavar="PATH",
        help="Custom path to the documents directory containing PDF files (default: app/data/LabDocs)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force download and extraction of LabDocs from Zenodo",
    )

    args = parser.parse_args()

    # Handle force download option
    if args.force_download:
        if args.doc_path:
            print("Warning: --force-download is ignored when --doc-path is specified.")
        else:
            print("Force downloading LabDocs...")
            # Download to app/data directory
            data_dir = Path(__file__).parent / "data"
            if download_labdocs(output_dir=data_dir):
                print("LabDocs download completed successfully.")
            else:
                print("Failed to download LabDocs.")
                sys.exit(1)
            return

    extract_labdocs(doc_path=args.doc_path)


if __name__ == "__main__":
    main()
