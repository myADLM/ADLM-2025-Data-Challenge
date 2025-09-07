from pathlib import Path
from tqdm import tqdm


def read_text_documents(base_dir: str | Path) -> list[tuple[str, str]]:
    """
    Read all text files from a base directory into a list of tuples.

    Args:
        base_dir: Base directory path to search for text files

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

    txt_files = list(base_dir.rglob("*.txt"))

    if not txt_files:
        print(f"No text files found in: {base_dir}")
        return []

    print(f"Found {len(txt_files)} text files to read")

    documents = []
    errors = []

    for file_path in tqdm(txt_files, desc="Reading text files"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

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
