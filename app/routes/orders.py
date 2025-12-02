from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.services.connection import get_db
from app.models.models import Order, OrderItem, Product, User
from app.routes.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str
    payment_method: str
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    shipping_address: str
    payment_method: str
    notes: Optional[str]
    created_at: datetime
    items: List[dict]
    
    class Config:
        from_attributes = True

@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    try:
        # Calculate total price
        total_price = 0.0
        order_items_data = []
        
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            price = item.price if item.price else float(product.price)
            total_price += price * item.quantity
            order_items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": price
            })
        
        # Create order
        new_order = Order(
            user_id=current_user["id"],
            total_price=total_price,
            status="pending",
            shipping_address=order_data.shipping_address,
            payment_method=order_data.payment_method,
            notes=order_data.notes
        )
        db.add(new_order)
        db.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                **item_data
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(new_order)
        
        return {
            "success": True,
            "message": "Order created successfully",
            "order_id": new_order.id,
            "total_price": total_price
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/my")
async def get_my_orders(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user"""
    try:
        orders = db.query(Order).filter(
            Order.user_id == current_user["id"]
        ).order_by(Order.created_at.desc()).all()
        
        result = []
        for order in orders:
            items = []
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                items.append({
                    "product_id": item.product_id,
                    "product_name": product.name if product else "Unknown",
                    "quantity": item.quantity,
                    "price": float(item.price)
                })
            
            result.append({
                "id": order.id,
                "total_price": float(order.total_price),
                "status": order.status,
                "shipping_address": order.shipping_address,
                "payment_method": order.payment_method,
                "notes": order.notes,
                "created_at": order.created_at.isoformat(),
                "items": items
            })
        
        return {"success": True, "orders": result}
    except Exception as e:
        logger.error(f"Get user orders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID"""
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user["id"]
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        items = []
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items.append({
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "price": float(item.price)
            })
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "total_price": float(order.total_price),
                "status": order.status,
                "shipping_address": order.shipping_address,
                "payment_method": order.payment_method,
                "notes": order.notes,
                "created_at": order.created_at.isoformat(),
                "items": items
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update order status (user can cancel, admin can update)"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Only allow user to cancel their own orders or admin to update any
        if order.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # User can only cancel
        if current_user.get("role") != "admin" and status != "cancelled":
            raise HTTPException(status_code=403, detail="Users can only cancel orders")
        
        order.status = status
        db.commit()
        
        return {
            "success": True,
            "message": "Order status updated",
            "order_id": order.id,
            "status": order.status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update order status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
