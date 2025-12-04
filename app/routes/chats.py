# app/routes/chats.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from sqlalchemy.orm import Session

from app.services.connection import get_db
from app.routes.auth import verify_token
from app.services import chat_service
from app.services.chatbot_service import chatbot_service
from app.models.models import Product

logger = logging.getLogger(__name__)

router = APIRouter()


# ====== REQUEST/RESPONSE MODELS ======

class CreateChatRequest(BaseModel):
    title: str


class UpdateChatRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    text: str
    disease_context: Optional[Dict] = None


class ChatSessionResponse(BaseModel):
    id: str
    user_id: int
    title: str
    created_at: str
    updated_at: str
    message_count: Optional[int] = None
    last_message: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    user_id: int
    text: str
    is_bot: bool
    timestamp: str
    products: Optional[List[Dict]] = None


class ChatListResponse(BaseModel):
    chats: List[ChatSessionResponse]


class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    bot_message: MessageResponse


# ====== CHAT SESSION ENDPOINTS ======

@router.get("/users/{user_id}/chats", response_model=ChatListResponse)
async def get_user_chats(
    user_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a user"""
    try:
        # Verify user can only access their own chats
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        chats = chat_service.get_user_chats(db, user_id)
        return {"chats": chats}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user chats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chats"
        )


@router.post("/users/{user_id}/chats", response_model=ChatSessionResponse)
async def create_chat(
    user_id: int,
    request: CreateChatRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create new chat session"""
    try:
        # Verify user can only create their own chats
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        chat = chat_service.create_chat_session(db, user_id, request.title)
        return chat
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat"
        )


@router.get("/chats/{chat_id}", response_model=ChatSessionResponse)
async def get_chat(
    chat_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get single chat session"""
    try:
        # Verify access
        if not chat_service.verify_chat_access(db, chat_id, current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        chat = chat_service.get_chat_session(db, chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        return {
            "id": chat.id,
            "user_id": chat.user_id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat"
        )


@router.put("/chats/{chat_id}", response_model=ChatSessionResponse)
async def update_chat(
    chat_id: str,
    request: UpdateChatRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update chat session title"""
    try:
        # Verify access
        if not chat_service.verify_chat_access(db, chat_id, current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        chat = chat_service.update_chat_session(db, chat_id, request.title)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        return chat
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat"
        )


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete chat session"""
    try:
        # Verify access
        if not chat_service.verify_chat_access(db, chat_id, current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        success = chat_service.delete_chat_session(db, chat_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat"
        )


# ====== CHAT MESSAGE ENDPOINTS ======

@router.get("/chats/{chat_id}/messages", response_model=MessagesListResponse)
async def get_messages(
    chat_id: str,
    limit: int = 50,
    offset: int = 0,
    order: str = "desc",
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get messages for a chat"""
    try:
        # Debug logging
        logger.info(f"Getting messages for chat {chat_id}, user {current_user['id']}")
        
        # Verify access
        if not chat_service.verify_chat_access(db, chat_id, current_user["id"]):
            # Check if chat exists
            chat = chat_service.get_chat_session(db, chat_id)
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
            logger.warning(f"Access denied: chat {chat_id} belongs to user {chat.user_id}, but user {current_user['id']} tried to access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Validate order
        if order not in ["asc", "desc"]:
            order = "desc"
        
        result = chat_service.get_chat_messages(db, chat_id, limit, offset, order)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch messages"
        )


@router.post("/chats/{chat_id}/messages", response_model=SendMessageResponse)
async def send_message(
    chat_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Send message and get AI response"""
    try:
        # Debug logging
        logger.info(f"Sending message to chat {chat_id}, user {current_user['id']}")
        
        # Verify access
        if not chat_service.verify_chat_access(db, chat_id, current_user["id"]):
            # Check if chat exists
            chat = chat_service.get_chat_session(db, chat_id)
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
            logger.warning(f"Access denied: chat {chat_id} belongs to user {chat.user_id}, but user {current_user['id']} tried to access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        user_id = current_user["id"]
        
        # Save user message
        user_message = chat_service.create_message(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            text=request.text,
            is_bot=False
        )
        
        # Get chat history for context
        history = chat_service.get_chat_history(db, chat_id, limit=10)
        
        # Get available products for recommendations
        products = db.query(Product).limit(50).all()
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price) if p.price else 0,
                "for_conditions": p.for_conditions or ""
            }
            for p in products
        ]
        
        # Get AI response
        ai_response = await chatbot_service.get_response(
            user_message=request.text,
            chat_history=history,
            disease_context=request.disease_context,
            available_products=product_list
        )
        
        # Save bot message
        bot_message = chat_service.create_message(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            text=ai_response["text"],
            is_bot=True,
            products=ai_response.get("products", [])
        )
        
        return {
            "user_message": user_message,
            "bot_message": bot_message
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )

@router.post("/chats/guest")
async def create_guest_chat(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """Create a guest chat session and get AI response without saving to DB"""
    try:
        # Create a temporary chat ID
        import uuid
        chat_id = str(uuid.uuid4())
        
        # Get AI response
        ai_response = await chatbot_service.get_response(
            user_message=request.text,
            chat_history=[],
            disease_context=request.disease_context,
            available_products=[]
        )
        
        return {
            "chat_id": chat_id,
            "response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Create guest chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create guest chat"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get single message"""
    try:
        message = chat_service.get_message(db, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Verify access through chat
        if not chat_service.verify_chat_access(db, message.chat_id, current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        result = {
            "id": message.id,
            "chat_id": message.chat_id,
            "user_id": message.user_id,
            "text": message.text,
            "is_bot": message.is_bot,
            "timestamp": message.timestamp.isoformat()
        }
        
        if message.products:
            result["products"] = message.products
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch message"
        )


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    try:
        message = chat_service.get_message(db, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Verify access through chat
        if not chat_service.verify_chat_access(db, message.chat_id, current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        success = chat_service.delete_message(db, message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )
