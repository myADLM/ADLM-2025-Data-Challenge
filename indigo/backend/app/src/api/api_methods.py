from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.src.api.api_objects import *
from app.src.chat.chat import chat
from app.src.search.search import Search


def download_document_impl(file_path: str, database_path: Path):
    """Securely download a document from the 'originals' directory."""
    print(f"PDF request received for: {file_path}")
    try:
        safe_path = _validate_document_path(file_path, database_path)
        print(f"Safe path: {safe_path}")
        print(f"File exists: {safe_path.exists()}")
        return FileResponse(
            path=safe_path, filename=safe_path.name, media_type="application/pdf"
        )
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def chat_impl(request: ChatRequest, search_client: Search, database_path: Path):
    """Process chat request and return response."""
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
    """Get list of safe documents from the originals directory."""
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
    """Validate that the requested document path is safe and exists in originals directory."""
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
