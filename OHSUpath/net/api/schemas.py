# net/api/schemas.py

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

AccessRole = Literal["owner", "editor", "viewer"]

class UserBrief(BaseModel):
    id: int
    email: str | None = None
    name: str | None = None

class SourceDocument(BaseModel):
    """Citation/source document reference"""
    doc_id: str  # Unique identifier for the document
    title: str  # Display name (filename)
    source_url: str  # URL to download the file (e.g., /api/files/{id}/download)
    page: int | None = None
    snippet: str | None = None  # Content preview/snippet
    mime_type: str | None = None  # File MIME type (optional)
    file_size: int | None = None  # File size in bytes (optional)

class MessageOut(BaseModel):
    role: str
    content: str
    created_at: int
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None
    sources: List[SourceDocument] = Field(default_factory=list)
    reasoning: str | None = None  # LLM reasoning from <think> tags

class ConversationOut(BaseModel):
    # Expose only public_chat_id externally
    id: str = Field(..., description="public_chat_id")
    title: str
    last_message_at: int
    created_at: int
    access_role: AccessRole = "owner"
    shared_by: UserBrief | None = None
    unread_count: int = 0

class ConversationWithMessages(ConversationOut):
    messages: List[MessageOut] = Field(default_factory=list)
    last_seen_at: int = 0

class ConversationPatch(BaseModel):
    title: str | None = None

# Sharing (reserved)
class ShareCreate(BaseModel):
    email: str
    role: Literal["editor", "viewer"] = "viewer"

class ShareUpdate(BaseModel):
    role: Literal["editor", "viewer"]

class ShareOut(BaseModel):
    user: UserBrief
    role: Literal["editor", "viewer"]
    invited_by: UserBrief
    created_at: int

# For old clients (optional)
class QueryRequest(BaseModel):
    q: str
    meta: Dict[str, Any] | None = None
