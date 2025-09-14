# net/api/routers/query.py

from __future__ import annotations
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..models import Conversation, ConversationMember, Message, now_ms

router = APIRouter(prefix="/query", tags=["query"])

# Allow multiple field names; the client may send public_id / id / conversation_id / chat_id
def _extract_public_id(body: dict) -> Optional[str]:
    for k in ("public_id", "id", "conversation_id", "chat_id"):
        v = body.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def _get_conv_by_public(db: Session, public_id: str) -> Conversation | None:
    return db.exec(select(Conversation).where(Conversation.public_chat_id == public_id)).first()

def _access_role(db: Session, conv: Conversation, uid: int) -> str | None:
    if conv.user_id == uid:
        return "owner"
    cm = db.exec(
        select(ConversationMember).where(
            ConversationMember.conversation_id == conv.id,
            ConversationMember.user_id == uid,
        )
    ).first()
    return cm.role if cm else None

class SendIn(BaseModel):
    content: str
    role: Optional[str] = "user"  # "user" | "system" | "assistant"
    # Compatible field names: public_id / id / conversation_id / chat_id
    public_id: Optional[str] = None
    id: Optional[str] = None
    conversation_id: Optional[str] = None
    chat_id: Optional[str] = None

class SendOut(BaseModel):
    role: str
    content: str
    created_at: int

# -- Non-streaming: POST /query --
@router.post("", response_model=SendOut, status_code=201)
def send_message(body: SendIn, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    public_id = _extract_public_id(body.dict())
    if not public_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing public_id")

    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

    role = _access_role(db, conv, user.id)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can write")

    ts = now_ms()
    # Save user message
    msg = Message(conversation_id=conv.id, role=body.role or "user", content=body.content, created_at=ts)
    db.add(msg)

    # Generate a simple assistant echo (placeholder)
    assistant_text = f"Echo: {body.content}"
    msg2 = Message(conversation_id=conv.id, role="assistant", content=assistant_text, created_at=ts + 1)
    db.add(msg2)

    # Update conversation timestamp
    conv.last_message_at = msg2.created_at
    db.add(conv)

    db.commit()

    return SendOut(role=msg2.role, content=msg2.content, created_at=msg2.created_at)

# -- Streaming: POST /query/stream --
def _sse_line(data: str) -> bytes:
    # SSE: each message ends with a blank line
    return f"data: {data}\n\n".encode("utf-8")

@router.post("/stream")
async def query_stream(body: SendIn, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    """
    Receive user message -> write to DB -> stream back an "assistant reply" (echo placeholder) ->
    after streaming completes, write the assistant message to DB and update the conversation timestamp.
    """
    public_id = _extract_public_id(body.dict())
    if not public_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing public_id")

    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

    role = _access_role(db, conv, user.id)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can write")

    # 1) Write the user message to DB first to avoid loss on refresh
    ts = now_ms()
    user_msg = Message(conversation_id=conv.id, role=body.role or "user", content=body.content, created_at=ts)
    db.add(user_msg)
    db.commit()

    # 2) Echo placeholder as the assistant reply
    full_reply = f"Echo: {body.content}"
    tokens = full_reply.split()

    async def event_gen() -> AsyncGenerator[bytes, None]:
        yield _sse_line('{"type":"start"}')
        assembled = []
        for i, t in enumerate(tokens):
            assembled.append(t + (" " if i < len(tokens) - 1 else ""))
            yield _sse_line(f'{{"type":"chunk","delta":"{t}{" " if i < len(tokens)-1 else ""}"}}')
        yield _sse_line('{"type":"done"}')

        # 3) Write the assistant message to DB and update the conversation timestamp
        try:
            ts2 = now_ms()
            assistant_msg = Message(conversation_id=conv.id, role="assistant", content="".join(assembled), created_at=ts2)
            db.add(assistant_msg)
            conv.last_message_at = ts2
            db.add(conv)
            db.commit()
        except Exception:
            pass

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
