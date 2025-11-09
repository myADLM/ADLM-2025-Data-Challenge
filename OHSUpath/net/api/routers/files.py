# net/api/routers/files.py

from __future__ import annotations
import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/files", tags=["files"])

# Get the data directory from config
# This matches the config.yaml data_dir setting
DATA_DIR = Path("data").resolve()


def safe_filename(filename: str) -> str:
    """
    Sanitize filename for Content-Disposition header.
    Removes control characters, newlines, and potentially dangerous characters.
    """
    # Remove control characters, newlines, and quotes
    safe = re.sub(r'[\x00-\x1f\x7f"\']', '', filename)
    # Limit length
    if len(safe) > 255:
        safe = safe[:255]
    return safe or "download.pdf"


@router.get("/{file_path:path}/download")
async def download_file(
    file_path: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Serve a file for inline viewing in browser.

    - Uses Content-Disposition: inline to display in browser tab
    - Opens PDF in browser's native viewer

    Args:
        file_path: Relative path within data directory (can include subdirectories)
        user: Current authenticated user

    Returns:
        StreamingResponse with the file for inline viewing only

    Raises:
        HTTPException: If file not found, access denied, or other errors
    """
    try:
        # Treat file_path as a relative path within DATA_DIR
        # Security: Ensure the file path doesn't escape the data directory
        full_path = (DATA_DIR / file_path).resolve()

        # Check that the resolved path is still within DATA_DIR
        if not str(full_path).startswith(str(DATA_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine MIME type
        suffix = full_path.suffix.lower()
        mime_type = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".json": "application/json",
            ".csv": "text/csv",
        }.get(suffix, "application/octet-stream")

        # Sanitize filename
        safe_name = safe_filename(full_path.name)

        # Stream the file
        def file_iterator():
            with open(full_path, "rb") as f:
                chunk_size = 65536  # 64KB chunks
                while chunk := f.read(chunk_size):
                    yield chunk

        # Use inline disposition to display in browser tab
        headers = {
            "Content-Disposition": f'inline; filename="{safe_name}"',
        }

        return StreamingResponse(
            file_iterator(),
            media_type=mime_type,
            headers=headers
        )

    except HTTPException:
        raise
    except ValueError as e:
        print(f"[FILES] Invalid path for file_path={file_path}: {e}")
        raise HTTPException(status_code=400, detail="Invalid file path")
    except Exception as e:
        print(f"[FILES] Error serving file {file_path}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error serving file")