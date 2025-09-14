# net/api/models.py

from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field
import time, secrets

def now_ms() -> int:
    return int(time.time() * 1000)

def new_public_id() -> str:
    # 64-byte hex (128-bit); extremely low collision probability
    return secrets.token_hex(32)

class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: Optional[str] = None
    password_hash: Optional[str] = None
    is_active: bool = True
    created_at: int = Field(default_factory=now_ms, index=True)

class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # Public chat id (not reversible), unique index
    public_chat_id: str = Field(
        default_factory=new_public_id, index=True,
        sa_column_kwargs={"unique": True}
    )
    title: str = Field(default="New Chat")
    last_message_at: int = Field(default_factory=now_ms, index=True)
    created_at: int = Field(default_factory=now_ms, index=True)

class Message(SQLModel, table=True):
    __tablename__ = "message"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str = Field(index=True)  # "user" | "assistant" | "system"
    content: str
    created_at: int = Field(default_factory=now_ms, index=True)

class LoginEvent(SQLModel, table=True):
    __tablename__ = "login_event"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    at: int = Field(default_factory=now_ms, index=True)
    ip: Optional[str] = None
    agent: Optional[str] = None

# === NEW: ConversationMember (for sharing/permissions) ===
class ConversationMember(SQLModel, table=True):
    __tablename__ = "conversation_member"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    # "owner" is represented by Conversation.user_id; members typically use "editor" or "viewer"
    role: str = Field(default="viewer", index=True)

    # Inviter (used for frontend display: shared_by)
    invited_by: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    created_at: int = Field(default_factory=now_ms, index=True)
