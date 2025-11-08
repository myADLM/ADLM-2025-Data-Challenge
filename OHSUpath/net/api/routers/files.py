# net/api/routers/files.py

from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/files", tags=["files"])

# Get the data directory from config
# This matches the config.yaml data_dir setting
DATA_DIR = Path("data").resolve()


@router.get("/document/{file_path:path}")
async def get_document(
    file_path: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Serve a document file to authenticated users.

    Args:
        file_path: Relative path to the file within the data directory
        user: Current authenticated user

    Returns:
        FileResponse with the requested document

    Raises:
        HTTPException: If file not found or path is invalid
    """
    # Security: Ensure the file path doesn't escape the data directory
    try:
        full_path = (DATA_DIR / file_path).resolve()

        # Check that the resolved path is still within DATA_DIR
        if not str(full_path).startswith(str(DATA_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        # Serve the file
        return FileResponse(
            path=str(full_path),
            media_type="application/pdf",
            filename=full_path.name
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    except Exception as e:
        print(f"[FILES] Error serving file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error serving file")