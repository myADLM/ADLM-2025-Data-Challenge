# net/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import select, Session
from ..db import get_db
from ..models import User, LoginEvent
from ..security import verify_password
from ..deps import require_internal_key
import time

router = APIRouter()

class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    id: int
    username: str
    email: str | None = None
    name: str | None = None

@router.post("/auth/login", response_model=LoginResp)
def login(
    req: LoginReq,
    request: Request,
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_internal_key),  # only allow gateway calls
):
    ident = (req.username or "").strip().lower()
    user = db.exec(select(User).where(User.email == ident)).first()

    if not user or not user.is_active or not verify_password(req.password, user.password_hash or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    evt = LoginEvent(
        user_id=user.id,
        at=int(time.time()),
        ip=(request.client.host if request.client else None),
        agent=request.headers.get("user-agent"),
    )
    db.add(evt)
    db.commit()

    display_username = user.name or (user.email.split("@")[0] if user.email else f"user{user.id}")
    return LoginResp(id=user.id, username=display_username, email=user.email, name=user.name)
