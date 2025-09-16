from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import polars as pl
import uvicorn
import os
from app.src.database.build_database import build_database
from app.src.api.api_objects import ChatRequest, ChatItem, ChatResponse, Document
from app.src.search.search import Search

def get_safe_document(database_path: Path, relative_path: str) -> Document:
    """Get list of safe documents from the originals directory."""
    file_path = database_path / "originals" / relative_path
    
    if file_path.exists():
        safe_url = f"/documents/{relative_path}"
        return Document(
            title=file_path.name,
            url=safe_url,
            ghost=relative_path
        )
    
    return Document(
        title="File not found",
        url=""
    )

def validate_document_path(requested_path: str, database_path: Path) -> Path:
    """Validate that the requested document path is safe and exists in originals directory."""
    # Remove leading slash and normalize path
    clean_path = requested_path.lstrip('/').replace('\\', '/')
    
    # Check for path traversal attempts
    if '..' in clean_path or clean_path.startswith('/'):
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
        raise HTTPException(status_code=400, detail="File path outside allowed directory")
    
    # Check if file exists
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if it's a PDF file
    if full_path.suffix.lower() != '.pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    return full_path

def main():

    app = FastAPI()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure the database is built
    zip_path = Path(__file__).parent / "input_data" / "raw_input_data.zip"
    database_path = Path(__file__).parent / "database"
    build_database(
        input_zip_path=zip_path,
        database_path=database_path
    )
    search_client = Search(pl.read_parquet(database_path / "medallions" / "silver.parquet"))

    # API Routes
    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.get("/documents/{file_path:path}")
    def download_document(file_path: str):
        """Securely download a document from the originals directory."""
        print(f"PDF request received for: {file_path}")
        try:
            safe_path = validate_document_path(file_path, database_path)
            print(f"Safe path: {safe_path}")
            print(f"File exists: {safe_path.exists()}")
            return FileResponse(
                path=safe_path,
                filename=safe_path.name,
                media_type='application/pdf'
            )
        except HTTPException as e:
            print(f"HTTPException: {e.detail}")
            raise
        except Exception as e:
            print(f"Exception: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        """Process chat request and return response."""
        # Get the last message from the user
        chat_items = request.chat_items
        latest_user_message = None
        for item in reversed(chat_items):
            if item.agent == "user":
                latest_user_message = item.text
                break
        if not latest_user_message:
            return ChatResponse(
                chat_items=chat_items,
                documents=[]
            )

        # TODO:Add assistant response
        chat_items.append(ChatItem(agent="assistant", text="I have no response, but here are some relevant documents."))
        
        doc_paths = search_client.search(latest_user_message)
        # Get safe documents from the originals directory
        documents = [get_safe_document(database_path, path) for path in doc_paths]
        
        return ChatResponse(
            chat_items=chat_items,
            documents=documents
        )

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=5174)

