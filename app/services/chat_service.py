from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

from app.models.models import ChatSession, ChatMessage, User


def generate_chat_id() -> str:
    """Generate unique chat session ID"""
    return f"chat_{uuid.uuid4().hex[:12]}"


def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg_{uuid.uuid4().hex[:12]}"


# ====== CHAT SESSION OPERATIONS ======

def get_user_chats(db: Session, user_id: int) -> List[Dict]:
    """Get all chat sessions for a user with message counts and last message"""
    chats = (
        db.query(
            ChatSession,
            func.count(ChatMessage.id).label('message_count'),
            func.max(ChatMessage.timestamp).label('last_message_time')
        )
        .outerjoin(ChatMessage, ChatSession.id == ChatMessage.chat_id)
        .filter(ChatSession.user_id == user_id)
        .group_by(ChatSession.id)
        .order_by(desc(ChatSession.updated_at))
        .all()
    )
    
    result = []
    for chat, message_count, last_message_time in chats:
        # Get last message text
        last_message = None
        if message_count > 0:
            last_msg = (
                db.query(ChatMessage)
                .filter(ChatMessage.chat_id == chat.id)
                .order_by(desc(ChatMessage.timestamp))
                .first()
            )
            if last_msg:
                last_message = last_msg.text
        
        result.append({
            "id": chat.id,
            "user_id": chat.user_id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat() if chat.created_at else None,
            "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
            "message_count": message_count,
            "last_message": last_message
        })
    
    return result


def create_chat_session(db: Session, user_id: int, title: str) -> Dict:
    """Create new chat session"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    chat_id = generate_chat_id()
    new_chat = ChatSession(
        id=chat_id,
        user_id=user_id,
        title=title,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    return {
        "id": new_chat.id,
        "user_id": new_chat.user_id,
        "title": new_chat.title,
        "created_at": new_chat.created_at.isoformat(),
        "updated_at": new_chat.updated_at.isoformat()
    }


def get_chat_session(db: Session, chat_id: str) -> Optional[ChatSession]:
    """Get single chat session"""
    return db.query(ChatSession).filter(ChatSession.id == chat_id).first()


def update_chat_session(db: Session, chat_id: str, title: str) -> Optional[Dict]:
    """Update chat session title"""
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        return None
    
    chat.title = title
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(chat)
    
    return {
        "id": chat.id,
        "user_id": chat.user_id,
        "title": chat.title,
        "created_at": chat.created_at.isoformat(),
        "updated_at": chat.updated_at.isoformat()
    }


def delete_chat_session(db: Session, chat_id: str) -> bool:
    """Delete chat session and all its messages"""
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        return False
    
    db.delete(chat)
    db.commit()
    return True


def verify_chat_access(db: Session, chat_id: str, user_id: int) -> bool:
    """Verify user has access to chat"""
    chat = db.query(ChatSession).filter(
        ChatSession.id == chat_id,
        ChatSession.user_id == user_id
    ).first()
    return chat is not None


# ====== CHAT MESSAGE OPERATIONS ======

def get_chat_messages(
    db: Session, 
    chat_id: str, 
    limit: int = 50, 
    offset: int = 0,
    order: str = "desc"
) -> Dict:
    """Get messages for a chat with pagination"""
    # Build query
    query = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id)
    
    # Count total
    total = query.count()
    
    # Apply ordering
    if order == "desc":
        query = query.order_by(desc(ChatMessage.timestamp))
    else:
        query = query.order_by(ChatMessage.timestamp)
    
    # Apply pagination
    messages = query.offset(offset).limit(limit).all()
    
    # Format messages
    message_list = []
    for msg in messages:
        message_data = {
            "id": msg.id,
            "chat_id": msg.chat_id,
            "user_id": msg.user_id,
            "text": msg.text,
            "is_bot": msg.is_bot,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        }
        
        # Add products if present
        if msg.products:
            message_data["products"] = msg.products
        
        message_list.append(message_data)
    
    # Calculate if there are more messages
    has_more = (offset + limit) < total
    
    return {
        "messages": message_list,
        "total": total,
        "has_more": has_more
    }


def create_message(
    db: Session,
    chat_id: str,
    user_id: int,
    text: str,
    is_bot: bool = False,
    products: Optional[List[Dict]] = None
) -> Dict:
    """Create a new message in a chat"""
    # Verify chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise ValueError(f"Chat {chat_id} not found")
    
    message_id = generate_message_id()
    new_message = ChatMessage(
        id=message_id,
        chat_id=chat_id,
        user_id=user_id,
        text=text,
        is_bot=is_bot,
        timestamp=datetime.now(timezone.utc),
        products=products
    )
    
    # Update chat session updated_at
    chat.updated_at = datetime.now(timezone.utc)
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    result = {
        "id": new_message.id,
        "chat_id": new_message.chat_id,
        "user_id": new_message.user_id,
        "text": new_message.text,
        "is_bot": new_message.is_bot,
        "timestamp": new_message.timestamp.isoformat()
    }
    
    if new_message.products:
        result["products"] = new_message.products
    
    return result


def get_message(db: Session, message_id: str) -> Optional[ChatMessage]:
    """Get single message"""
    return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()


def delete_message(db: Session, message_id: str) -> bool:
    """Delete a message"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        return False
    
    db.delete(message)
    db.commit()
    return True


def get_chat_history(db: Session, chat_id: str, limit: int = 10) -> List[Dict]:
    """Get recent chat history for AI context"""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(desc(ChatMessage.timestamp))
        .limit(limit)
        .all()
    )
    
    # Reverse to get chronological order
    messages.reverse()
    
    return [
        {
            "role": "model" if msg.is_bot else "user",
            "parts": [msg.text]
        }
        for msg in messages
    ]
