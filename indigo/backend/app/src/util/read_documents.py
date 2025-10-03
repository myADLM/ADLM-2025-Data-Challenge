import shutil
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm

from app.src.util.file_reader_registry import read_file_with_registry


def extract_zip(
    zip_path: str | Path, output_dir: str | Path, force_rebuild: bool = False
) -> bool:
    """
    Extract a zip file to the specified output directory.

    Args:
        zip_path: Path to the zip file to extract.
        output_dir: Directory to extract the zip file contents to.
        force_rebuild: Whether to force rebuild the output directory.

    Returns:
        True on success, False otherwise.
    """
    # Convert to Path objects
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)

    # Check if zip file exists and is a file
    if not zip_path.exists():
        print(f"Error: Zip file not found: {zip_path}")
        return False

    if not zip_path.is_file():
        print(f"Error: Expected a file, but found a directory at: {zip_path}")
        return False

    if not force_rebuild and output_dir.exists():
        print(f"Skipping zip extraction. Output directory already exists: {output_dir}")
        return True

    # Remove output directory if it exists
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Extracting {zip_path} to {output_dir}...")

        # Synchronously extract; this blocks until unzip completes
        result = subprocess.run(
            ["unzip", "-o", str(zip_path), "-d", str(output_dir)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("Error extracting file:")
            print(result.stdout)
            print(result.stderr)
            return False

        print(f"Successfully extracted {zip_path} to {output_dir}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during extraction: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def read_documents_as_plaintext(
    base_dir: str | Path, file_extensions: list[str] = [".txt", ".md", ".rst", ".pdf"]
) -> list[tuple[str, str]]:
    """
    Read all files from a base directory into a list of tuples. Files are read as plain text.

    Args:
        base_dir: Base directory path to search for files
        file_extensions: List of file extensions to read

    Returns:
        List of tuples, where each tuple contains (document_path, document_content)
        - document_path: String relative path to the text file (relative to base_dir)
        - document_content: String content of the text file

    Raises:
        FileNotFoundError: If the base directory doesn't exist
        Exception: If there are errors reading individual files

    Example:
        # Read all text files from extracted docs
        documents = read_text_documents("app/data/extracted_docs")
        for doc_path, doc_content in documents:
            print(f"File: {doc_path}")  # e.g., "FDA/Cardiovascular/doc1.txt"
            print(f"Content: {doc_content[:100]}...")
    """
    base_dir = Path(base_dir)

    if not base_dir.exists():
        raise FileNotFoundError(f"Base directory not found: {base_dir}")

    if not base_dir.is_dir():
        raise ValueError(f"Path is not a directory: {base_dir}")

    # Collect all files matching provided extensions (case-insensitive)
    exts = {ext.lower() for ext in file_extensions}
    files = [p for p in base_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]

    if not files:
        print(f"No text files found in: {base_dir}")
        return []

    print(f"Found {len(files)} text files to read")

    documents = []
    errors = []

    for file_path in tqdm(files, desc="Reading text files"):
        try:
            content = read_file_with_registry(file_path).strip()

            if content:
                # Return tuple of (relative_path, content) instead of full path
                relative_path = file_path.relative_to(base_dir)
                documents.append((str(relative_path), content))
            else:
                print(f"Warning: Empty file: {file_path}")

        except Exception as e:
            error_msg = f"Error reading {file_path}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            continue

    print(f"Successfully read {len(documents)} text documents")
    if errors:
        print(f"Encountered {len(errors)} errors during reading")

    return documents


def read_text_documents(base_dir: str | Path) -> list[tuple[str, str]]:
    """
    Backwards-compatible wrapper to read only .txt files.

    This preserves existing behavior expected by callers that import
    read_text_documents, while the more general function
    read_documents_as_plaintext allows custom extensions.
    """
    return read_documents_as_plaintext(base_dir, file_extensions=[".txt"])
