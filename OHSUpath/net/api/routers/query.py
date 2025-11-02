# net/api/routers/query.py

from __future__ import annotations
from typing import Optional, AsyncGenerator
import json
from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_db, engine
from ..deps import get_current_user, CurrentUser
from ..models import Conversation, ConversationMember, Message, now_ms
from ..rag_service import get_rag_service

router = APIRouter(prefix="/query", tags=["query"])


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


class SourceDocument(BaseModel):
    source: str
    page: int | str | None = None
    content_preview: str | None = None


def _sse(reply: str, sources: list[dict] | None = None, llm_enabled: bool | None = None) -> AsyncGenerator[bytes, None]:
    async def gen():
        # Stream the main content character by character
        for ch in reply:
            yield f"data: {ch}\n\n".encode("utf-8")

        # Send sources as a separate event
        if sources:
            print(f"[SSE] Sending sources event with {len(sources)} sources")
            sources_json = json.dumps(sources)
            print(f"[SSE] Sources JSON: {sources_json[:200]}...")
            yield f"event: sources\ndata: {sources_json}\n\n".encode("utf-8")
        else:
            print("[SSE] No sources to send")

        # Send metadata (llm_enabled status)
        if llm_enabled is not None:
            print(f"[SSE] Sending metadata event: llm_enabled={llm_enabled}")
            metadata_json = json.dumps({"llm_enabled": llm_enabled})
            yield f"event: metadata\ndata: {metadata_json}\n\n".encode("utf-8")

        print("[SSE] Sending done event")
        yield b"event: done\ndata: ok\n\n"
    return gen()


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


def _extract_public_id(body: dict) -> Optional[str]:
    for k in ("public_id", "id", "conversation_id", "chat_id"):
        v = body.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

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
    db.add(Message(conversation_id=conv.id, role=body.role or "user", content=body.content, created_at=ts))

    assistant_text = f"Echo: {body.content}"
    ts2 = ts + 1
    db.add(Message(conversation_id=conv.id, role="assistant", content=assistant_text, created_at=ts2))
    conv.last_message_at = ts2
    db.add(conv)
    db.commit()

    return SendOut(role="assistant", content=assistant_text, created_at=ts2)


@router.post("/stream")
async def query_stream(body: SendIn, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    public_id = _extract_public_id(body.dict())
    if not public_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing public_id")
    return await stream_query(public_id, body, db, user)


class StreamBody(BaseModel):
    content: str
    role: Optional[str] = "user"


@router.post("/stream/{public_id}")
async def stream_query(
    public_id: str = Path(...),
    body: StreamBody | SendIn | None = None,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if not body or not (body.content or "").strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="content required")

    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")

    role = _access_role(db, conv, user.id)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # persist user message and bump last_message_at
    t = now_ms()
    db.add(Message(conversation_id=conv.id, role=(getattr(body, "role", None) or "user"), content=body.content, created_at=t))
    conv.last_message_at = t
    db.add(conv)
    db.commit()

    # Get AI response from RAG service
    rag_service = get_rag_service()
    result = rag_service.query(body.content)

    reply = result.get("answer", "No answer generated.")
    source_docs = result.get("source_documents", [])
    llm_enabled = result.get("llm_enabled", False)

    # Format sources for frontend
    sources_list = []
    for doc in source_docs[:5]:  # Limit to top 5 sources
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page_number") or doc.metadata.get("page", "?")
        content_preview = doc.page_content[:200] if hasattr(doc, 'page_content') else ""
        sources_list.append({
            "source": source,
            "page": page,
            "content_preview": content_preview
        })

    # Save conversation ID before session closes
    conv_id = conv.id

    async def gen():
        async for chunk in _sse(reply, sources=sources_list, llm_enabled=llm_enabled):
            yield chunk

        # Create NEW session for persisting after stream (avoid DetachedInstanceError)
        t2 = now_ms()
        with Session(engine) as new_db:
            db_msg = Message(conversation_id=conv_id, role="assistant", content=reply, created_at=t2)
            new_db.add(db_msg)
            db_conv = new_db.get(Conversation, conv_id)
            if db_conv:
                db_conv.last_message_at = t2
                new_db.add(db_conv)
            new_db.commit()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)
