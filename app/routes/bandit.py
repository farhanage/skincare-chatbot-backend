# app/routes/bandit.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.services.connection import get_db
from app.routes.auth import verify_token
from app.services.bandit_service import ThompsonSamplingBandit

logger = logging.getLogger(__name__)

router = APIRouter()

class UpdateBanditRequest(BaseModel):
    product_id: int
    reward: float
    impression_count: int = 1


class BanditRecommendationResponse(BaseModel):
    success: bool
    recommendations: List[Dict[str, Any]]
    algorithm: str = "Thompson Sampling"


@router.get("/bandit/recommend", response_model=BanditRecommendationResponse)
async def get_bandit_recommendations(
    n_recommendations: int = 5,
    category: Optional[str] = None,
    exclude_product_ids: Optional[List[int]] = Query(None),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get product recommendations using Thompson Sampling Multi-Armed Bandit
    
    This endpoint uses Thompson Sampling to balance exploration and exploitation,
    recommending products that are likely to maximize user engagement based on
    historical interaction data.
    
    Args:
        n_recommendations: Number of products to recommend (default: 5)
        category: Optional category filter
        exclude_product_ids: Optional list of product IDs to exclude
    
    Returns:
        List of recommended products with Thompson sampling scores and bandit statistics
    """
    try:
        bandit = ThompsonSamplingBandit(db)
        
        recommendations = bandit.recommend_products(
            n_recommendations=n_recommendations,
            category=category,
            exclude_product_ids=exclude_product_ids
        )
        
        logger.info(
            f"User {current_user['id']} requested {n_recommendations} "
            f"bandit recommendations, returned {len(recommendations)}"
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "algorithm": "Thompson Sampling"
        }
        
    except Exception as e:
        logger.error(f"Bandit recommendation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/bandit/update")
async def update_bandit_state(
    request: UpdateBanditRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Update bandit state after showing a product to user
    
    This should be called when:
    1. A product is shown to the user (impression_count=1, reward based on action)
    2. User interacts with the product (reward based on interaction type)
    
    Reward values:
    - Click: 1.0
    - Add to cart: 2.0
    
    Args:
        product_id: ID of the product
        reward: Reward value from the interaction
        impression_count: Number of impressions (default: 1)
    """
    try:
        bandit = ThompsonSamplingBandit(db)
        
        bandit.update_bandit_state(
            product_id=request.product_id,
            reward=request.reward,
            impression_count=request.impression_count
        )
        
        logger.info(
            f"User {current_user['id']} - Updated bandit for product {request.product_id} "
            f"with reward {request.reward}"
        )
        
        return {
            "success": True,
            "message": "Bandit state updated successfully",
            "product_id": request.product_id
        }
        
    except Exception as e:
        logger.error(f"Update bandit state error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update bandit state: {str(e)}"
        )


@router.get("/bandit/statistics")
async def get_bandit_statistics(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get overall Thompson Sampling bandit statistics
    
    Returns aggregated statistics about the bandit algorithm performance,
    including total impressions, rewards, and average parameters.
    """
    try:
        bandit = ThompsonSamplingBandit(db)
        stats = bandit.get_bandit_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "algorithm": "Thompson Sampling"
        }
        
    except Exception as e:
        logger.error(f"Get bandit statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bandit statistics: {str(e)}"
        )


@router.get("/bandit/product/{product_id}")
async def get_product_bandit_state(
    product_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get bandit state for a specific product
    
    Returns the current Thompson Sampling parameters and statistics
    for a specific product.
    """
    try:
        from app.models.models import BanditState, Product
        
        # Check if product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get bandit state
        state = db.query(BanditState).filter(
            BanditState.product_id == product_id
        ).first()
        
        if not state:
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product.name,
                "bandit_state": {
                    "impressions": 0,
                    "rewards": 0,
                    "alpha": 1.0,
                    "beta": 1.0,
                    "expected_reward": 0.5,
                    "note": "No interactions yet (using prior)"
                }
            }
        
        expected_reward = float(state.alpha) / (float(state.alpha) + float(state.beta))
        
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.name,
            "bandit_state": {
                "impressions": state.impressions,
                "rewards": float(state.rewards),
                "alpha": float(state.alpha),
                "beta": float(state.beta),
                "expected_reward": expected_reward,
                "last_updated": state.last_updated.isoformat() if state.last_updated else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product bandit state error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product bandit state: {str(e)}"
        )
