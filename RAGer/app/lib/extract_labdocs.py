import pdfplumber
import fitz
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Protocol, Dict, Type
from tqdm import tqdm
import sys
from app.lib.data_source import download_labdocs


class FileReader(Protocol):
    """Protocol for file readers."""

    def read(self, file_path: str | Path) -> str:
        """Read the contents of a file."""
        ...


class FileReaderRegistry:
    """Registry for file readers based on file extensions."""

    _readers: Dict[str, Type[FileReader]] = {}

    @classmethod
    def register(cls, *extensions: str):
        """
        Decorator to register a file reader class for specific file extensions.
        Only one reader per extension is allowed.

        Args:
            extensions: List of file extensions (e.g., ['.txt', '.md'])
        """

        def decorator(reader_class: Type[FileReader]) -> Type[FileReader]:
            for ext in extensions:
                # Normalize extension to lowercase and ensure it starts with '.'
                normalized_ext = ext.lower()
                if not normalized_ext.startswith("."):
                    normalized_ext = "." + normalized_ext

                # Check if extension is already registered
                if normalized_ext in cls._readers:
                    existing_reader = cls._readers[normalized_ext]
                    print(
                        f"Warning: Extension {normalized_ext} already registered with {existing_reader.__name__}"
                    )
                    print(f"Replacing with {reader_class.__name__}")

                cls._readers[normalized_ext] = reader_class
                print(
                    f"Registered {reader_class.__name__} for extension: {normalized_ext}"
                )

            return reader_class

        return decorator

    @classmethod
    def get_reader(cls, file_path: str | Path) -> FileReader:
        """
        Get the appropriate reader for a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            FileReader instance for the file type

        Raises:
            ValueError: If no reader is registered for the file extension
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        if extension not in cls._readers:
            raise ValueError(f"No reader registered for extension: {extension}")

        reader_class = cls._readers[extension]
        return reader_class()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return list(cls._readers.keys())

    @classmethod
    def is_supported(cls, file_path: str | Path) -> bool:
        """Check if a file type is supported."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in cls._readers


@FileReaderRegistry.register(".txt", ".md", ".rst")
class TextFileReader:
    """Reader for text files."""

    def read(self, file_path: str | Path) -> str:
        """Read the contents of a text file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading text file {file_path}: {str(e)}")


@FileReaderRegistry.register(".pdf")
class PDFFileReader:
    """Reader for PDF files."""

    def read(self, file_path: str | Path) -> str:
        """Read the contents of a PDF file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            return self.pdf_plumber_read(file_path)

        except Exception as pdfplumber_error:
            print(f"pdfplumber failed for {file_path}: {pdfplumber_error}")
            try:
                return self.pymupdf_read(file_path)
            except Exception as fitz_error:
                print(f"PyMuPDF failed for {file_path}: {fitz_error}")
                try:
                    return self.ocr_read(file_path)
                except Exception as ocr_error:
                    print(f"OCR failed for {file_path}: {ocr_error}")
                    raise Exception(f"All readers failed for {file_path}")

    def pdf_plumber_read(self, file_path: str | Path) -> str:
        """Read the contents of a PDF file using pdfplumber."""
        with pdfplumber.open(file_path) as pdf:
            all_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

            extracted_text = all_text.strip()
            if extracted_text:
                return extracted_text
            else:
                raise Exception("pdfplumber returned empty content")

    def pymupdf_read(self, file_path: str | Path) -> str:
        """Read the contents of a PDF file using PyMuPDF."""
        doc = fitz.open(file_path)
        all_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                all_text += text + "\n"

        doc.close()
        extracted_text = all_text.strip()

        if extracted_text:
            print(f"PyMuPDF fallback succeeded for {file_path}")
            return extracted_text
        else:
            raise Exception("PyMuPDF returned empty content")

    def ocr_read(self, file_path: str | Path) -> str:
        """Read the contents of a PDF file using OCR."""
        all_text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=300)  # render page as image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                if text:
                    all_text += text + "\n"
        return all_text.strip()


def read_file_with_registry(file_path: str | Path) -> str:
    """
    Read a file using the appropriate registered reader.

    Args:
        file_path: Path to the file to read

    Returns:
        String content of the file

    Raises:
        ValueError: If no reader is registered for the file type
        Exception: If there's an error reading the file
    """
    if not FileReaderRegistry.is_supported(file_path):
        supported = FileReaderRegistry.get_supported_extensions()
        raise ValueError(f"Unsupported file type. Supported extensions: {supported}")

    reader = FileReaderRegistry.get_reader(file_path)
    return reader.read(file_path)


def extract_labdocs(doc_path: str = None):
    """Entry point for the text extraction script.

    Args:
        doc_path: Optional custom path to the documents directory.
                 If not provided, defaults to "LabDocs" in the app/data folder.

    Note:
        This function can be called directly or through the Poetry script.
        For command line usage with arguments, use: poetry run extract_labdocs --help
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

    print(f"Starting LabDocs extraction...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    try:
        extract_labdoc_file_dataset(input_dir, output_dir)
        print("LabDocs extraction completed successfully!")
    except Exception as e:
        print(f"Error during LabDocs extraction: {e}")
        sys.exit(1)


def extract_labdoc_file_dataset(
    base_input_path: str | Path, base_output_path: str | Path
) -> None:
    """
    Recursively search for files in base_input_path and extract text to base_output_path
    while preserving the directory structure.

    Args:
        base_input_path: Root directory to search for files
        base_output_path: Root directory to output extracted text files
    """
    base_input_path = Path(base_input_path)
    base_output_path = Path(base_output_path)

    # Create output directory if it doesn't exist
    base_output_path.mkdir(parents=True, exist_ok=True)

    files = [file for file in base_input_path.rglob("*") if file.is_file()]
    print(f"Found {len(files)} PDF files to process")
    for file in tqdm(files, desc="Processing PDFs"):
        try:
            relative_path = file.relative_to(base_input_path)
            output_file = base_output_path / relative_path.with_suffix(".txt")

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

    print(f"Completed processing")


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
