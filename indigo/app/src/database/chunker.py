import shutil
from chonkie import SentenceChunker
from app.lib.util.read_text_documents import read_text_documents
from pathlib import Path
from tqdm import tqdm


def chunk_docs(docs_path: Path, chunked_docs_path: Path):
    """
    Recursively search for files in docs_path, apply SentenceChunker to each file,
    and save chunks to chunked_docs_path with the same relative path structure.

    For each file in docs_path, chunked_docs_path will contain a directory with the file name
    and write a file for each chunk called chunk_<N>.txt

    Any existing files in chunked_docs_path will be removed before processing.

    Args:
        docs_path: Path to the directory containing documents to chunk
        chunked_docs_path: Path to the output directory for chunked documents
    """
    # Ensure input path exists
    if not docs_path.exists():
        raise FileNotFoundError(f"Input directory '{docs_path}' does not exist")

    # Remove existing files in chunked_docs_path if it exists
    if chunked_docs_path.exists():
        shutil.rmtree(chunked_docs_path)
        print(f"Cleared existing chunked documents from {chunked_docs_path}")

    # Create output directory
    chunked_docs_path.mkdir(parents=True, exist_ok=True)

    # Initialize the chunker
    chunker = SentenceChunker()

    # Get all text documents
    input_docs = read_text_documents(docs_path)

    # Process each file
    for relative_path, text_content in tqdm(input_docs, desc="Chunking documents"):
        try:
            # Convert relative_path to Path object if it's a string
            if isinstance(relative_path, str):
                relative_path = Path(relative_path)

            file_path = docs_path / relative_path

            # Create output directory structure
            # Remove file extension and create directory named after the file
            file_name = file_path.stem
            output_dir = chunked_docs_path / relative_path.parent / file_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Skip empty files
            if not text_content.strip():
                print(f"Warning: Skipping empty file {file_path}")
                continue

            # Split the text into chunks
            chunks = chunker(text_content)

            # Save each chunk as a separate file
            for i, chunk in enumerate(chunks):
                chunk_file = output_dir / f"chunk_{i:03d}.txt"
                with open(chunk_file, "w", encoding="utf-8") as f:
                    f.write(chunk.text)

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue

    print(f"Chunking completed. Output saved to: {chunked_docs_path}")
