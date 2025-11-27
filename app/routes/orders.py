from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os

router = APIRouter()

# Simple file-based storage for orders
ORDERS_FILE = "orders_data.json"

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    product_brand: str
    price: int
    quantity: int

class ShippingAddress(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    province: str
    postal_code: Optional[str] = ""

class OrderCreate(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str
    total_amount: int
    status: str = "pending"

class Order(BaseModel):
    id: str
    user_id: int
    user_name: str
    user_email: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str
    total_amount: int
    status: str
    created_at: str
    updated_at: str

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

@router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    """Create a new order"""
    try:
        orders = load_orders()
        
        # Generate order ID
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        new_order = {
            "id": order_id,
            "user_id": order_data.user_id,
            "user_name": order_data.user_name,
            "user_email": order_data.user_email,
            "items": [item.dict() for item in order_data.items],
            "shipping_address": order_data.shipping_address.dict(),
            "payment_method": order_data.payment_method,
            "total_amount": order_data.total_amount,
            "status": order_data.status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        orders.append(new_order)
        save_orders(orders)
        
        return new_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/user/{user_id}", response_model=List[Order])
async def get_user_orders(user_id: int):
    """Get all orders for a specific user"""
    try:
        orders = load_orders()
        user_orders = [order for order in orders if order["user_id"] == user_id]
        # Sort by created_at descending (newest first)
        user_orders.sort(key=lambda x: x["created_at"], reverse=True)
        return user_orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get a specific order by ID"""
    try:
        orders = load_orders()
        order = next((o for o in orders if o["id"] == order_id), None)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """Update order status"""
    try:
        orders = load_orders()
        order_index = next((i for i, o in enumerate(orders) if o["id"] == order_id), None)
        
        if order_index is None:
            raise HTTPException(status_code=404, detail="Order not found")
        
        orders[order_index]["status"] = status
        orders[order_index]["updated_at"] = datetime.now().isoformat()
        
        save_orders(orders)
        return orders[order_index]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
