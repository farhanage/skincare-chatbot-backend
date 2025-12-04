# app/routes/interactions.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timezone

from app.services.connection import get_db
from app.routes.auth import verify_token
from app.models.models import UserInteraction, Product
from app.services.bandit_service import ThompsonSamplingBandit

logger = logging.getLogger(__name__)

router = APIRouter()


class TrackInteractionRequest(BaseModel):
    product_id: int
    action: str  # 'click', 'add_to_cart'
    reward: Optional[float] = None  # If not provided, will be auto-calculated


class InteractionResponse(BaseModel):
    success: bool
    message: str
    interaction_id: Optional[int] = None


@router.post("/interactions/track", response_model=InteractionResponse)
async def track_interaction(
    request: TrackInteractionRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Track user interaction with products
    
    Actions and default rewards:
    - 'click': 1.0
    - 'add_to_cart': 2.0
    - custom: use provided reward value
    """
    try:
        user_id = current_user["id"]
        
        # Verify product exists
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Auto-calculate reward if not provided
        if request.reward is None:
            reward_map = {
                'click': 1.0,
                'add_to_cart': 2.0,
            }
            reward = reward_map.get(request.action.lower(), 0)
        else:
            reward = request.reward
        
        # Create interaction record
        interaction = UserInteraction(
            user_id=user_id,
            product_id=request.product_id,
            action=request.action,
            reward=reward,
            timestamp=datetime.now(timezone.utc)
        )
        
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        # Update bandit state with the interaction
        try:
            bandit = ThompsonSamplingBandit(db)
            bandit.update_bandit_state(
                product_id=request.product_id,
                reward=reward,
                impression_count=1
            )
            logger.info(f"Bandit state updated for product {request.product_id}")
        except Exception as bandit_error:
            logger.error(f"Failed to update bandit state: {bandit_error}")
            # Don't fail the interaction tracking if bandit update fails
        
        logger.info(
            f"User {user_id} - {request.action} on product {request.product_id} "
            f"(reward: {reward})"
        )
        
        return {
            "success": True,
            "message": "Interaction tracked successfully",
            "interaction_id": interaction.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Track interaction error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track interaction: {str(e)}"
        )


@router.get("/interactions/user")
async def get_user_interactions(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get interaction history for current user"""
    try:
        user_id = current_user["id"]
        
        # Query interactions with pagination
        interactions = (
            db.query(UserInteraction)
            .filter(UserInteraction.user_id == user_id)
            .order_by(UserInteraction.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        total = db.query(UserInteraction).filter(UserInteraction.user_id == user_id).count()
        
        # Format response
        interaction_list = [
            {
                "id": i.id,
                "product_id": i.product_id,
                "action": i.action,
                "reward": float(i.reward),
                "timestamp": i.timestamp.isoformat() if i.timestamp else None
            }
            for i in interactions
        ]
        
        return {
            "success": True,
            "interactions": interaction_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Get user interactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interactions: {str(e)}"
        )


@router.get("/interactions/product/{product_id}")
async def get_product_interactions(
    product_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all interactions for a specific product (admin/analytics)"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Query interactions
        interactions = (
            db.query(UserInteraction)
            .filter(UserInteraction.product_id == product_id)
            .order_by(UserInteraction.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        total = db.query(UserInteraction).filter(UserInteraction.product_id == product_id).count()
        
        # Format response
        interaction_list = [
            {
                "id": i.id,
                "user_id": i.user_id,
                "action": i.action,
                "reward": float(i.reward),
                "timestamp": i.timestamp.isoformat() if i.timestamp else None
            }
            for i in interactions
        ]
        
        # Calculate statistics
        from sqlalchemy import func
        stats = db.query(
            UserInteraction.action,
            func.count(UserInteraction.id).label('count'),
            func.sum(UserInteraction.reward).label('total_reward')
        ).filter(
            UserInteraction.product_id == product_id
        ).group_by(UserInteraction.action).all()
        
        action_stats = {
            stat.action: {
                "count": stat.count,
                "total_reward": float(stat.total_reward or 0)
            }
            for stat in stats
        }
        
        return {
            "success": True,
            "product_id": product_id,
            "interactions": interaction_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "statistics": action_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product interactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product interactions: {str(e)}"
        )
