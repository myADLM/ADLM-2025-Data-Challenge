import pdfplumber
import fitz
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Protocol, Dict, Type
from tqdm import tqdm
import sys
from app.lib.text_extraction.text_extraction import read_file_with_registry


def extract_docs(doc_path: str, database_dir: str):
    """
    Extract text from PDF documents and save to output directory.

    Recursively search for files in the input directory and extract text to the output directory
    while preserving the directory structure.

    Args:
        doc_path: Path to the documents directory.
        database_dir: Path to the output directory for extracted text files.
    """
    # Define input and output directories
    input_dir = Path(doc_path).resolve()
    if not input_dir.exists():
        print(f"Error: Specified document path '{input_dir}' does not exist.")
        sys.exit(1)

    output_dir = Path(database_dir).resolve() / "extracted_docs"

    print(f"Starting LabDocs extraction...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    try:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        files = [file for file in input_dir.rglob("*") if file.is_file()]
        print(f"Found {len(files)} PDF files to process")

        for file in tqdm(files, desc="Processing PDFs"):
            try:
                relative_path = file.relative_to(input_dir)
                output_file = output_dir / relative_path.with_suffix(".txt")

                # Check if output file already exist and is not empty
                if output_file.exists() and output_file.stat().st_size > 0:
                    continue

                text_content = read_file_with_registry(file)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text_content)

            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
                continue

        print("LabDocs extraction completed successfully!")
        print(f"Completed processing")

    except Exception as e:
        print(f"Error during LabDocs extraction: {e}")
        sys.exit(1)
