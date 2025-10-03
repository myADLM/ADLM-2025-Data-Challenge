from pathlib import Path
from typing import Dict, Protocol, Type

import fitz
import pytesseract
from PIL import Image

fitz.TOOLS.mupdf_display_errors(False)


class _FileReader(Protocol):
    """Protocol for file readers."""

    def read(self, file_path: str | Path) -> str:
        """Read the contents of a file."""
        ...


class _FileReaderRegistry:
    """Registry for file readers based on file extensions."""

    _readers: Dict[str, Type[_FileReader]] = {}

    @classmethod
    def register(cls, *extensions: str):
        """
        Decorator to register a file reader class for specific file extensions.
        Only one reader per extension is allowed.

        Args:
            extensions: List of file extensions (e.g., ['.txt', '.md'])
        """

        def decorator(reader_class: Type[_FileReader]) -> Type[_FileReader]:
            for ext in extensions:
                # Normalize extension to lowercase and ensure it starts with '.'
                normalized_ext = ext.lower()
                if not normalized_ext.startswith("."):
                    normalized_ext = "." + normalized_ext

                # Check if extension is already registered
                if normalized_ext in cls._readers:
                    existing_reader = cls._readers[normalized_ext]
                    raise ValueError(
                        f"Extension {normalized_ext} already registered with {existing_reader.__name__}"
                    )

                cls._readers[normalized_ext] = reader_class

            return reader_class

        return decorator

    @classmethod
    def get_reader(cls, file_path: str | Path) -> _FileReader:
        """
        Get the appropriate reader for a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            _FileReader instance for the file type

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


@_FileReaderRegistry.register(".txt", ".md", ".rst")
class _TextFileReader:
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


@_FileReaderRegistry.register(".pdf")
class _PDF_FileReader:
    """Reader for PDF files."""

    def read(self, file_path: str | Path) -> str:
        """Read the contents of a PDF file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        doc = fitz.open(file_path)
        all_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            try:
                text = page.get_text()
                if text:
                    all_text += text + "\n"
                else:
                    raise Exception("PyMuPDF returned empty page.")
            except Exception as e:
                print(f"Trying OCR to extract page {page_num+1} from {file_path}.")
                pix = page.get_pixmap(dpi=300)  # render page as image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                if text:
                    print("Success.")
                    all_text += text + "\n"
                else:
                    print("OCR failed.")

        doc.close()
        extracted_text = all_text.strip()

        if extracted_text:
            return extracted_text
        else:
            raise Exception(f"Failed to extract text from {file_path}")


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
    if not _FileReaderRegistry.is_supported(file_path):
        supported = _FileReaderRegistry.get_supported_extensions()
        raise ValueError(f"Unsupported file type. Supported extensions: {supported}")

    reader = _FileReaderRegistry.get_reader(file_path)
    return reader.read(file_path)
