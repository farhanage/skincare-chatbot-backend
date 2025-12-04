# app/services/bandit_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
import numpy as np
import logging
from datetime import datetime, timezone

from app.models.models import BanditState, Product, UserInteraction

logger = logging.getLogger(__name__)


class ThompsonSamplingBandit:
    """Thompson Sampling Multi-Armed Bandit for product recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _ensure_bandit_state(self, product_id: int) -> BanditState:
        """Ensure bandit state exists for a product"""
        state = self.db.query(BanditState).filter(
            BanditState.product_id == product_id
        ).first()
        
        if not state:
            state = BanditState(
                product_id=product_id,
                impressions=0,
                rewards=0,
                alpha=1,
                beta=1
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        
        return state
    
    def update_bandit_state(
        self,
        product_id: int,
        reward: float,
        impression_count: int = 1
    ) -> None:
        """
        Update bandit state after user interaction
        
        Args:
            product_id: Product that was shown/interacted with
            reward: Reward value from the interaction (0-3)
            impression_count: Number of times shown (default: 1)
        """
        from decimal import Decimal
        
        state = self._ensure_bandit_state(product_id)
        
        # Update impressions and rewards (convert to proper types)
        state.impressions += impression_count
        state.rewards = float(state.rewards) + float(reward)
        
        # Update Beta distribution parameters
        # Alpha: successes (normalized rewards)
        # Beta: failures (impressions - normalized rewards)
        
        # Normalize reward to [0, 1] range (assuming max reward is 3)
        normalized_reward = min(float(reward) / 3.0, 1.0)
        
        state.alpha = float(state.alpha) + normalized_reward
        state.beta = float(state.beta) + (1 - normalized_reward)
        state.last_updated = datetime.now(timezone.utc)
        
        self.db.commit()
        
        logger.info(
            f"Updated bandit state for product {product_id}: "
            f"alpha={state.alpha:.2f}, beta={state.beta:.2f}, "
            f"impressions={state.impressions}, rewards={state.rewards}"
        )
    
    def get_thompson_samples(
        self,
        product_ids: List[int]
    ) -> Dict[int, float]:
        """
        Generate Thompson samples for products
        
        Args:
            product_ids: List of product IDs to sample
            
        Returns:
            Dictionary mapping product_id to sampled theta value
        """
        samples = {}
        
        for product_id in product_ids:
            state = self._ensure_bandit_state(product_id)
            
            # Sample from Beta distribution
            alpha = float(state.alpha)
            beta = float(state.beta)
            
            # Sample theta from Beta(alpha, beta)
            theta = np.random.beta(alpha, beta)
            samples[product_id] = theta
        
        return samples
    
    def recommend_products(
        self,
        n_recommendations: int = 5,
        category: str = None,
        exclude_product_ids: List[int] = None
    ) -> List[Dict]:
        """
        Get product recommendations using Thompson Sampling
        
        Args:
            n_recommendations: Number of products to recommend
            category: Optional category filter
            exclude_product_ids: Optional list of product IDs to exclude
            
        Returns:
            List of recommended products with metadata
        """
        # Build query for available products
        query = self.db.query(Product)
        
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        if exclude_product_ids:
            query = query.filter(Product.id.notin_(exclude_product_ids))
        
        products = query.all()
        
        if not products:
            logger.warning("No products available for recommendations")
            return []
        
        # Get product IDs
        product_ids = [p.id for p in products]
        
        # Generate Thompson samples
        samples = self.get_thompson_samples(product_ids)
        
        # Sort products by sampled theta (descending)
        sorted_product_ids = sorted(
            samples.keys(),
            key=lambda pid: samples[pid],
            reverse=True
        )[:n_recommendations]
        
        # Get product details and bandit stats
        recommendations = []
        for product_id in sorted_product_ids:
            product = next((p for p in products if p.id == product_id), None)
            if not product:
                continue
            
            state = self.db.query(BanditState).filter(
                BanditState.product_id == product_id
            ).first()
            
            recommendations.append({
                "id": product.id,
                "name": product.name,
                "description": product.description or "",
                "price": float(product.price) if product.price else 0,
                "category": product.category or "",
                "image_url": product.image_url or "",
                "for_conditions": product.for_conditions or "",
                "thompson_sample": float(samples[product_id]),
                "bandit_stats": {
                    "impressions": state.impressions if state else 0,
                    "rewards": float(state.rewards) if state else 0,
                    "alpha": float(state.alpha) if state else 1.0,
                    "beta": float(state.beta) if state else 1.0,
                    "expected_reward": (
                        float(state.alpha) / (float(state.alpha) + float(state.beta))
                        if state else 0.5
                    )
                } if state else None
            })
        
        logger.info(
            f"Generated {len(recommendations)} Thompson Sampling recommendations"
        )
        
        return recommendations
    
    def get_bandit_statistics(self) -> Dict:
        """Get overall bandit statistics"""
        from sqlalchemy import func
        
        stats = self.db.query(
            func.count(BanditState.product_id).label('total_products'),
            func.sum(BanditState.impressions).label('total_impressions'),
            func.sum(BanditState.rewards).label('total_rewards'),
            func.avg(BanditState.alpha).label('avg_alpha'),
            func.avg(BanditState.beta).label('avg_beta')
        ).first()
        
        return {
            "total_products": stats.total_products or 0,
            "total_impressions": int(stats.total_impressions or 0),
            "total_rewards": float(stats.total_rewards or 0),
            "average_alpha": float(stats.avg_alpha or 1),
            "average_beta": float(stats.avg_beta or 1),
            "average_reward_rate": (
                float(stats.total_rewards) / int(stats.total_impressions)
                if stats.total_impressions else 0
            )
        }
