# net/api/routers/conversations.py

from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy import delete, func
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..models import (
    Conversation, ConversationMember, ConversationViewState,
    Message, User, now_ms
)
from ..schemas import (
    ConversationOut, ConversationWithMessages, ConversationPatch,
    UserBrief, ShareCreate, ShareOut, ShareUpdate
)

router = APIRouter()

def _brief(u: User | None) -> UserBrief | None:
    if not u:
        return None
    return UserBrief(id=u.id, email=u.email, name=u.name)

def _get_conv_by_public(db: Session, public_id: str) -> Conversation | None:
    return db.exec(select(Conversation).where(Conversation.public_chat_id == public_id)).first()

def _access_role(db: Session, conv: Conversation, uid: int) -> str | None:
    if conv.user_id == uid:
        return "owner"
    m = db.exec(
        select(ConversationMember)
        .where(ConversationMember.conversation_id == conv.id, ConversationMember.user_id == uid)
    ).first()
    return (m.role if m else None)

def _shared_by(db: Session, conv_id: int, uid: int) -> User | None:
    m = db.exec(
        select(ConversationMember)
        .where(ConversationMember.conversation_id == conv_id, ConversationMember.user_id == uid)
    ).first()
    if not m:
        return None
    return db.get(User, m.invited_by) if m.invited_by else None

def _get_last_seen(db: Session, conv_id: int, uid: int) -> int:
    vs = db.exec(
        select(ConversationViewState).where(
            ConversationViewState.conversation_id == conv_id,
            ConversationViewState.user_id == uid
        )
    ).first()
    return int(vs.last_seen_at) if vs else 0

def _set_last_seen(db: Session, conv_id: int, uid: int, ts: int) -> None:
    vs = db.exec(
        select(ConversationViewState).where(
            ConversationViewState.conversation_id == conv_id,
            ConversationViewState.user_id == uid
        )
    ).first()
    if vs:
        if ts > (vs.last_seen_at or 0):
            vs.last_seen_at = ts
            db.add(vs)
            db.commit()
    else:
        db.add(ConversationViewState(conversation_id=conv_id, user_id=uid, last_seen_at=ts))
        db.commit()

def _count_unread(db: Session, conv_id: int, last_seen: int) -> int:
    row = db.exec(
        select(func.count(Message.id)).where(
            Message.conversation_id == conv_id,
            Message.created_at > (last_seen or 0)
        )
    ).first()
    try:
        return int(row[0] if isinstance(row, (tuple, list)) else row)
    except Exception:
        return 0

@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)

    owned = db.exec(select(Conversation).where(Conversation.user_id == uid)).all()

    members = db.exec(select(ConversationMember).where(ConversationMember.user_id == uid)).all()
    by_cid = {m.conversation_id: m for m in (members or [])}
    shared_ids = list(by_cid.keys())
    shared_convs = db.exec(select(Conversation).where(Conversation.id.in_(shared_ids))).all() if shared_ids else []

    items: list[ConversationOut] = []

    # owned
    for c in owned:
        last_seen = _get_last_seen(db, c.id, uid)
        unread = _count_unread(db, c.id, last_seen)
        items.append(ConversationOut(
            id=c.public_chat_id, title=c.title,
            last_message_at=c.last_message_at, created_at=c.created_at,
            access_role="owner", shared_by=None, unread_count=unread
        ))

    # shared (sort by activity since invited)
    for c in shared_convs:
        m = by_cid.get(c.id)
        effective_last = max(int(c.last_message_at or 0), int(m.created_at if m else 0))
        inviter = _shared_by(db, c.id, uid)
        role = m.role if m else "viewer"
        last_seen = _get_last_seen(db, c.id, uid)
        unread = _count_unread(db, c.id, last_seen)
        items.append(ConversationOut(
            id=c.public_chat_id, title=c.title,
            last_message_at=effective_last, created_at=c.created_at,
            access_role=role, shared_by=_brief(inviter), unread_count=unread
        ))

    items.sort(key=lambda x: (x.last_message_at, x.created_at), reverse=True)
    return items

@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = Conversation(user_id=uid, title="New Chat")
    db.add(conv); db.commit(); db.refresh(conv)
    return ConversationOut(
        id=conv.public_chat_id, title=conv.title,
        last_message_at=conv.last_message_at, created_at=conv.created_at,
        access_role="owner", shared_by=None, unread_count=0
    )

@router.get("/conversations/{public_id}", response_model=ConversationWithMessages)
def get_conversation(public_id: str = Path(...), db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")

    msgs = db.exec(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at.asc())
    ).all()
    inviter = None if role == "owner" else _shared_by(db, conv.id, uid)
    last_seen = _get_last_seen(db, conv.id, uid)
    unread = _count_unread(db, conv.id, last_seen)

    # Build message list with user info
    import json
    msg_list = []
    for m in msgs:
        msg_dict = {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
            "user_id": m.user_id
        }
        # Fetch user name/email if user_id exists
        if m.user_id:
            u = db.get(User, m.user_id)
            if u:
                msg_dict["user_name"] = u.name
                msg_dict["user_email"] = u.email

        # Parse sources if available
        if hasattr(m, 'sources_json') and m.sources_json:
            try:
                msg_dict["sources"] = json.loads(m.sources_json)
            except Exception as e:
                print(f"[CONV] Error parsing sources for message {m.id}: {e}")
                msg_dict["sources"] = []

        msg_list.append(msg_dict)

    return ConversationWithMessages(
        id=conv.public_chat_id, title=conv.title,
        last_message_at=conv.last_message_at, created_at=conv.created_at,
        access_role=role, shared_by=_brief(inviter),
        messages=msg_list,
        last_seen_at=last_seen, unread_count=unread
    )

@router.patch("/conversations/{public_id}", response_model=ConversationOut)
def rename_conversation(public_id: str, patch: ConversationPatch, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can rename")

    if patch.title and patch.title.strip():
        conv.title = patch.title.strip()
        db.add(conv); db.commit(); db.refresh(conv)

    inviter = None if role == "owner" else _shared_by(db, conv.id, uid)
    last_seen = _get_last_seen(db, conv.id, uid)
    unread = _count_unread(db, conv.id, last_seen)
    return ConversationOut(
        id=conv.public_chat_id, title=conv.title,
        last_message_at=conv.last_message_at, created_at=conv.created_at,
        access_role=role, shared_by=_brief(inviter), unread_count=unread
    )

@router.delete("/conversations/{public_id}", status_code=204)
def delete_conversation(public_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        return
    role = _access_role(db, conv, uid)
    if role != "owner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner can delete")

    db.exec(delete(ConversationMember).where(ConversationMember.conversation_id == conv.id))
    db.exec(delete(ConversationViewState).where(ConversationViewState.conversation_id == conv.id))
    db.exec(delete(Message).where(Message.conversation_id == conv.id))
    db.delete(conv)
    db.commit()
    return

# Mark read up to "latest known on server" (compat)
@router.post("/conversations/{public_id}/read", status_code=204)
def mark_read(public_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")

    ts = max(now_ms(), int(conv.last_message_at or 0))
    _set_last_seen(db, conv.id, uid, ts)
    return

# NEW: Mark read up to a specific timestamp you actually rendered
class ReadToBody(BaseModel):
    last_seen_at: int

@router.post("/conversations/{public_id}/read_to", status_code=204)
def mark_read_to(public_id: str, body: ReadToBody, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")

    # Clamp to latest message time to avoid setting into the future
    latest = int(conv.last_message_at or 0)
    ts = int(body.last_seen_at or 0)
    if ts <= 0:
        return
    if ts > latest:
        ts = latest
    _set_last_seen(db, conv.id, uid, ts)
    return

# ==== Share APIs (unchanged except for unread fields already handled above) ====

@router.get("/conversations/{public_id}/shares", response_model=List[ShareOut])
def list_shares(public_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can view members")

    items = db.exec(select(ConversationMember).where(ConversationMember.conversation_id == conv.id)).all()
    out: list[ShareOut] = []
    for m in items:
        u = db.get(User, m.user_id); inv = db.get(User, m.invited_by) if m.invited_by else None
        if u and inv:
            out.append(ShareOut(user=_brief(u), role=m.role, invited_by=_brief(inv), created_at=m.created_at))
    return out

@router.post("/conversations/{public_id}/shares", status_code=204)
def add_share(public_id: str, body: ShareCreate, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can share")

    target = db.exec(select(User).where(User.email == body.email.lower().strip())).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if target.id == conv.user_id:
        return

    existing = db.exec(
        select(ConversationMember).where(ConversationMember.conversation_id == conv.id, ConversationMember.user_id == target.id)
    ).first()
    if existing:
        existing.role = body.role
        db.add(existing)
    else:
        db.add(ConversationMember(conversation_id=conv.id, user_id=target.id, role=body.role, invited_by=uid))
    db.commit()
    return

@router.patch("/conversations/{public_id}/shares/{target_user_id}", status_code=204)
def update_share(public_id: str, target_user_id: int, body: ShareUpdate, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    role = _access_role(db, conv, uid)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can update share")
    if target_user_id == conv.user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot change owner")

    m = db.exec(
        select(ConversationMember).where(ConversationMember.conversation_id == conv.id, ConversationMember.user_id == target_user_id)
    ).first()
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found")
    m.role = body.role
    db.add(m); db.commit()
    return

@router.delete("/conversations/{public_id}/shares/{target_user_id}", status_code=204)
def remove_share(public_id: str, target_user_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    uid = int(user.id)
    conv = _get_conv_by_public(db, public_id)
    if not conv:
        return
    role = _access_role(db, conv, uid)
    if role not in ("owner", "editor"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only owner/editor can remove share")
    if target_user_id == conv.user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot remove owner")

    db.exec(
        delete(ConversationMember).where(
            ConversationMember.conversation_id == conv.id,
            ConversationMember.user_id == target_user_id
        )
    )
    db.commit()
    return
