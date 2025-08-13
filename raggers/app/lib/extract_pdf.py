import pdfplumber
from pathlib import Path
from typing import Optional
from tqdm import tqdm
import sys
from app.lib.data_source import download_labdocs


def extract_pdfs(doc_path: str = None):
    """Entry point for the PDF extraction script.

    Args:
        doc_path: Optional custom path to the documents directory.
                 If not provided, defaults to "LabDocs" in the app/data folder.

    Note:
        This function can be called directly or through the Poetry script.
        For command line usage with arguments, use: poetry run extract_pdfs --help
    """
    current_dir = Path(__file__).parent

    # Define input and output directories
    if doc_path:
        input_dir = Path(doc_path).resolve()
        if not input_dir.exists():
            print(f"Error: Specified document path '{input_dir}' does not exist.")
            sys.exit(1)
    else:
        # Check if LabDocs exists in data directory, download if not
        data_dir = current_dir.parent / "data"
        input_dir = data_dir / "LabDocs"
        if not input_dir.exists():
            print("LabDocs directory not found at default location.")
            if not download_labdocs():
                print(
                    "Failed to download LabDocs. Please download manually or specify a custom \
                     path using --doc-path."
                )
                sys.exit(1)
            # Verify the directory now exists
            if not input_dir.exists():
                print(
                    "Error: LabDocs directory still not found after download attempt."
                )
                sys.exit(1)

    # Output directory is now in app/data/extracted_docs
    data_dir = current_dir.parent / "data"
    output_dir = data_dir / "extracted_docs"

    print(f"Starting PDF extraction...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    try:
        extract_pdf_file_dataset(input_dir, output_dir)
        print("PDF extraction completed successfully!")
    except Exception as e:
        print(f"Error during PDF extraction: {e}")
        sys.exit(1)


def extract_pdf_text_simple(pdf_path: str | Path) -> str:
    """
    PDF text extraction that returns all text as one string.

    Args:
        pdf_path: Path to the PDF file (string or Path object)

    Returns:
        String containing all extracted text
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
            return all_text.strip()

    except Exception as e:
        raise Exception(f"Error reading PDF file {pdf_path}: {str(e)}")


def extract_pdf_file_dataset(
    base_input_path: str | Path, base_output_path: str | Path
) -> None:
    """
    Recursively search for PDF files in base_input_path and extract text to base_output_path
    while preserving the directory structure.

    Args:
        base_input_path: Root directory to search for PDF files
        base_output_path: Root directory to output extracted text files
    """
    base_input_path = Path(base_input_path)
    base_output_path = Path(base_output_path)

    # Create output directory if it doesn't exist
    base_output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(base_input_path.rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process")
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            relative_path = pdf_file.relative_to(base_input_path)
            output_file = base_output_path / relative_path.with_suffix(".txt")

            # Check if output file already exists
            if output_file.exists():
                continue

            text_content = extract_pdf_text_simple(pdf_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text_content)

        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
            continue

    print(f"Completed processing ")
