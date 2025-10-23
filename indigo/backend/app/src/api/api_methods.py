import logging
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.src.api.api_objects import *
from app.src.chat.chat import chat
from app.src.search.search import Search

logger = logging.getLogger("app")


def download_document_impl(file_path: str, database_path: Path) -> FileResponse:
    """
    Download a document from the 'originals' directory.

    This function provides secure access to PDF documents stored in the originals
    directory. It performs comprehensive path validation to prevent directory
    traversal attacks and ensures only valid PDF files can be accessed.

    Args:
        file_path (str): The relative path to the document within the originals directory.
                        Should not contain leading slashes or path traversal sequences.
        database_path (Path): The base path to the database directory containing the
                            originals subdirectory.

    Returns:
        FileResponse: A FastAPI FileResponse object containing the PDF file with
                     appropriate headers for download.

    Raises:
        HTTPException: 400 if the file path is invalid or contains path traversal attempts.
        HTTPException: 404 if the requested file does not exist.
        HTTPException: 400 if the file is not a PDF.
        HTTPException: 500 if an unexpected error occurs during processing.

    Example:
        >>> database_path = Path("/data/database")
        >>> response = download_document_impl("LabDocs/FDA/Cardiovascular/K221640.pdf", database_path)
        >>> print(response.filename)  # "K221640.pdf"

    Note:
        The function logs all requests and validation steps for debugging purposes.
        Only PDF files are allowed for download.
    """
    logger.info(f"PDF request received for: {file_path}")
    try:
        safe_path = _validate_document_path(file_path, database_path)
        logger.debug(f"Safe path: {safe_path}")
        logger.debug(f"File exists: {safe_path.exists()}")
        return FileResponse(
            path=safe_path, filename=safe_path.name, media_type="application/pdf"
        )
    except HTTPException as e:
        logger.warning(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def chat_impl(request: ChatRequest, search_client: Search, database_path: Path) -> ChatResponse:
    """
    Process chat request and return AI-generated response with relevant documents.
    
    This function handles the complete chat processing pipeline, including:
    1. Extracting the latest user message from the conversation
    2. Performing document search based on the user's query
    3. Generating an AI response using the specified model
    4. Retrieving and formatting relevant documents with matching text chunks
    
    Args:
        request (ChatRequest): The chat request containing conversation history,
                             query model, and search type preferences.
        search_client (Search): The search client instance for document retrieval.
        database_path (Path): The base path to the database directory containing
                            the originals subdirectory for document access.
    
    Returns:
        ChatResponse: A response object containing the updated conversation with
                     the AI's reply and a list of relevant documents with their
                     matching text chunks.
    
    Raises:
        Exception: Any exception raised during search or chat processing will be
                  propagated to the caller.
    
    Example:
        >>> request = ChatRequest(
        ...     chat_items=[ChatItem(role="user", text="What is cardiovascular testing?")],
        ...     query_model="gpt-5",
        ...     search_type="rank_fusion"
        ... )
        >>> search_client = Search()
        >>> database_path = Path("/data/database")
        >>> response = chat_impl(request, search_client, database_path)
        >>> print(response.chat_items[-1].text)  # AI response
        >>> print(len(response.documents))  # Number of relevant documents
    
    Note:
        If no user message is found in the chat history, returns the original
        chat items with an empty document list. The function processes the
        conversation in chronological order and appends the AI response.
    """
    # Get the last message from the user
    chat_items = request.chat_items
    query_model = request.query_model
    search_type = request.search_type

    latest_user_message = None
    for item in reversed(chat_items):
        if item.role == "user":
            latest_user_message = item.text
            break
    if not latest_user_message:
        return ChatResponse(chat_items=chat_items, documents=[])

    # Run the search algorithm
    context_records = search_client.search(latest_user_message, search_type)
    chat_items.append(
        ChatItem(
            role=RoleType.ASSISTANT,
            text=chat(query_model, chat_items, context_records),
        )
    )

    doc_infos = {}
    for chunk in context_records:
        doc_infos[chunk["file_path"]] = doc_infos.get(chunk["file_path"], []) + [
            chunk["chunk_text"]
        ]

    # Get safe documents from the originals directory
    documents = [
        _get_safe_document(database_path, (file_path, matches))
        for file_path, matches in doc_infos.items()
    ]

    return ChatResponse(chat_items=chat_items, documents=documents)


def _get_safe_document(
    database_path: Path, doc_info: tuple[str, list[str]]
) -> Document:
    """Create a Document object from file path and matching text chunks."""
    file_path, matches = doc_info
    relative_path = file_path

    full_path = database_path / "originals" / relative_path

    if full_path.exists():
        safe_url = f"/documents/{relative_path}"
        return Document(
            title=full_path.name, url=safe_url, ghost=relative_path, matches=matches
        )

    return Document(title="File not found", url="", ghost="", matches=[])


def _validate_document_path(requested_path: str, database_path: Path) -> Path:
    """Validate document path for security and return safe absolute path.
    
    Raises:
        HTTPException: 400 for invalid paths or non-PDF files, 404 for missing files.
    """
    # Remove leading slash and normalize path
    clean_path = requested_path.lstrip("/").replace("\\", "/")

    # Check for path traversal attempts
    if ".." in clean_path or clean_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Construct full path within originals directory
    originals_path = database_path / "originals"
    full_path = originals_path / clean_path

    # Ensure the file is within the originals directory
    try:
        full_path = full_path.resolve()
        originals_path = originals_path.resolve()
        full_path.relative_to(originals_path)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="File path outside allowed directory"
        )

    # Check if file exists
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Check if it's a PDF file
    if full_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    return full_path
