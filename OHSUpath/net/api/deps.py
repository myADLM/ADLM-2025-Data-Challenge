# net/api/deps.py

from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from pydantic import BaseModel
from .settings import settings

class CurrentUser(BaseModel):
    id: int  # Use int to avoid issues when comparing with DB integer columns
    email: Optional[str] = None
    name: Optional[str] = None

def require_internal_key(x_internal_key: Optional[str] = Header(default=None)):
    # Use 403 to reflect "authenticated but not authorized" semantics
    if not x_internal_key or x_internal_key != settings.INTERNAL_SHARED_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal key")
    return True

def get_current_user(
    _ok: bool = Depends(require_internal_key),
    x_user_id: Optional[str] = Header(default=None)
) -> CurrentUser:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user")
    try:
        uid = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad user id")
    return CurrentUser(id=uid)
