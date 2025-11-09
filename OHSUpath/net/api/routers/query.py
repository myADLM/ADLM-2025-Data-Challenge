# net/api/routers/query.py

from __future__ import annotations
from typing import Optional, AsyncGenerator
import json
import asyncio
from pathlib import Path as PathLib
from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.requests import Request
from ..db import get_db, engine
from ..deps import get_current_user, CurrentUser
from ..models import Conversation, ConversationMember, Message, now_ms
from ..rag_service import get_rag_service

# Get the data directory (same as in files.py)
DATA_DIR = PathLib("data").resolve()

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
    doc_id: str
    title: str
    source_url: str
    page: int | None = None
    snippet: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


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
    public_id = _extract_public_id(body.model_dump())
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
    public_id = _extract_public_id(body.model_dump())
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
    db.add(Message(
        conversation_id=conv.id,
        role=(getattr(body, "role", None) or "user"),
        content=body.content,
        created_at=t,
        user_id=user.id
    ))
    conv.last_message_at = t
    db.add(conv)
    db.commit()

    # Get AI response from RAG service
    try:
        rag_service = get_rag_service()
        result = rag_service.query(body.content)

        reply = result.get("answer", "No answer generated.")
        source_docs = result.get("source_documents", [])
        llm_enabled = result.get("llm_enabled", False)

        print(f"[QUERY] Got {len(source_docs)} source documents from RAG service")

        # Format sources for frontend with error handling
        # Deduplicate by filename to show each file only once
        sources_dict = {}  # filename -> source info

        for idx, doc in enumerate(source_docs):
            try:
                # Safely get metadata
                metadata = getattr(doc, 'metadata', {})
                if not isinstance(metadata, dict):
                    print(f"[QUERY] Warning: doc {idx} has non-dict metadata: {type(metadata)}")
                    metadata = {}

                source_path = metadata.get("source", "unknown")
                page_num = metadata.get("page_number") or metadata.get("page")

                # Convert page to int or None
                try:
                    page = int(page_num) if page_num is not None else None
                except (ValueError, TypeError):
                    page = None

                # Extract filename
                filename = source_path.split('/')[-1] if '/' in source_path else source_path.split('\\')[-1] if '\\' in source_path else source_path

                # Calculate relative path from DATA_DIR
                try:
                    source_path_obj = PathLib(source_path).resolve()
                    # Get relative path from DATA_DIR
                    relative_path = str(source_path_obj.relative_to(DATA_DIR))
                    print(f"[QUERY] Converted {source_path} -> relative: {relative_path}")
                except (ValueError, OSError) as e:
                    # Fallback: if path is not relative to DATA_DIR, try multiple strategies
                    print(f"[QUERY] Warning: Could not make path relative to DATA_DIR: {e}")

                    # Strategy 1: Check if it's relative to project root (OHSUpath/)
                    try:
                        source_path_obj = PathLib(source_path).resolve()
                        project_root = DATA_DIR.parent  # OHSUpath directory
                        rel_from_project = str(source_path_obj.relative_to(project_root))
                        # If this path starts with something other than 'data/', prepend 'data/'
                        # (handles case where RAG stored path as /path/to/OHSUpath/tiny/file.pdf)
                        if not rel_from_project.startswith('data'):
                            relative_path = 'data/' + rel_from_project
                            print(f"[QUERY] Adjusted path from project root: {relative_path}")
                        else:
                            # Path already includes data/, extract just the part after data/
                            relative_path = rel_from_project[5:] if rel_from_project.startswith('data/') else rel_from_project
                            print(f"[QUERY] Extracted from project root: {relative_path}")
                    except (ValueError, OSError) as e2:
                        # Strategy 2: Simple string replacement
                        print(f"[QUERY] Could not extract from project root either: {e2}, using string replacement")
                        relative_path = source_path.replace('data/', '').replace('data\\', '').replace(str(DATA_DIR) + '/', '').replace(str(DATA_DIR) + '\\', '')
                        # If still absolute, try to extract just the filename or last path components
                        if '/' in relative_path or '\\' in relative_path:
                            parts = relative_path.replace('\\', '/').split('/')
                            # Take last 2 parts (e.g., tiny/filename.pdf)
                            relative_path = '/'.join(parts[-2:]) if len(parts) >= 2 else parts[-1]
                        print(f"[QUERY] Fallback relative path: {relative_path}")

                # Safely get content
                snippet = ""
                if hasattr(doc, 'page_content'):
                    try:
                        snippet = str(doc.page_content)[:200]
                    except Exception as e:
                        print(f"[QUERY] Error getting page_content for doc {idx}: {e}")

                # If we haven't seen this file yet, add it
                if filename not in sources_dict:
                    sources_dict[filename] = {
                        "doc_id": relative_path,  # Use relative path as doc_id
                        "title": filename,
                        "source_url": f"/api/files/{relative_path}/download",
                        "page": page,
                        "snippet": snippet,
                        "mime_type": "application/pdf" if filename.lower().endswith('.pdf') else None,
                        "file_size": None  # Could add file size lookup if needed
                    }
                    print(f"[QUERY] Added source {len(sources_dict)}: {filename}, page {page}, url: /api/files/{relative_path}/download")
            except Exception as e:
                print(f"[QUERY] Error processing doc {idx}: {e}")
                import traceback
                traceback.print_exc()
                continue

        # Convert to list (limit to top 5 unique files)
        sources_list = list(sources_dict.values())[:5]
        print(f"[QUERY] Formatted {len(sources_list)} unique sources for frontend (from {len(source_docs)} total chunks)")
    except Exception as e:
        print(f"[QUERY] Error in RAG query: {e}")
        import traceback
        traceback.print_exc()
        reply = f"Error processing query: {str(e)}"
        sources_list = []
        llm_enabled = False

    # Save conversation ID before session closes
    conv_id = conv.id

    async def gen():
        try:
            # Stream the response with error handling
            async for chunk in _sse(reply, sources=sources_list, llm_enabled=llm_enabled):
                yield chunk
        except asyncio.CancelledError:
            print("[SSE] Client disconnected (CancelledError)")
            return
        except Exception as e:
            print(f"[SSE] Error while streaming: {e}")
            import traceback
            traceback.print_exc()
            # Don't re-raise; just stop the stream to avoid 500
            return

        # Persist assistant message after streaming completes
        try:
            t2 = now_ms()
            with Session(engine) as new_db:
                # Serialize sources to JSON for storage (ensure plain dicts)
                sources_json_str = json.dumps(sources_list) if sources_list else None

                db_msg = Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=reply,
                    created_at=t2,
                    sources_json=sources_json_str
                )
                new_db.add(db_msg)
                db_conv = new_db.get(Conversation, conv_id)
                if db_conv:
                    db_conv.last_message_at = t2
                    new_db.add(db_conv)
                new_db.commit()
                print(f"[QUERY] Saved assistant message with {len(sources_list)} sources")
        except Exception as e:
            print(f"[QUERY] Persist error: {e}")
            import traceback
            traceback.print_exc()
            # Don't re-raise - message was already streamed to client

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)
