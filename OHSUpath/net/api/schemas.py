# net/api/schemas.py

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

AccessRole = Literal["owner", "editor", "viewer"]

class UserBrief(BaseModel):
    id: int
    email: str | None = None
    name: str | None = None

class MessageOut(BaseModel):
    role: str
    content: str
    created_at: int

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
