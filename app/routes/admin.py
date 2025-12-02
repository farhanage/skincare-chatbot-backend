# app/routes/admin.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from datetime import datetime
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.routes.auth import verify_token
from app.services.auth_db import get_user_by_id
from app.services.connection import get_db_context, get_db
from app.models.models import User, CartItem, Product, Order, OrderItem

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_admin(current_user: dict = Depends(verify_token)) -> dict:
    """Verify if user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/debug/info")
async def debug_info(admin: dict = Depends(verify_admin)):
    """Get system debug information"""
    try:
        from app.database.connection import DATABASE_URL, engine
        
        info = {
            "timestamp": datetime.now().isoformat(),
            "admin_user": admin["username"],
            "database": {
                "url": DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL,  # Hide credentials
                "connected": engine.pool.checkedout() == 0
            }
        }
        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"Debug info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/users")
async def debug_users(admin: dict = Depends(verify_admin)):
    """Get all users (admin only)"""
    try:
        with get_db_context() as db:
            users = db.query(User).order_by(User.created_at.desc()).all()
            
            return {
                "success": True,
                "count": len(users),
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role,
                        "created_at": user.created_at.isoformat()
                    }
                    for user in users
                ]
            }
    except Exception as e:
        logger.error(f"Debug users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/products")
async def debug_products(admin: dict = Depends(verify_admin)):
    """Get all products from database (admin only)"""
    try:
        with get_db_context() as db:
            products = db.query(Product).all()
            
            return {
                "success": True,
                "count": len(products),
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "price": product.price,
                        "category": product.category
                    }
                    for product in products
                ]
            }
    except Exception as e:
        logger.error(f"Debug products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/carts")
async def debug_carts(admin: dict = Depends(verify_admin)):
    """Get all cart items (admin only)"""
    try:
        with get_db_context() as db:
            cart_items = db.query(CartItem).join(User).order_by(CartItem.added_at.desc()).all()
            
            return {
                "success": True,
                "count": len(cart_items),
                "carts": [
                    {
                        "id": item.id,
                        "user_id": item.user_id,
                        "username": item.user.username,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "added_at": item.added_at.isoformat()
                    }
                    for item in cart_items
                ]
            }
    except Exception as e:
        logger.error(f"Debug carts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/orders")
async def debug_orders(admin: dict = Depends(verify_admin)):
    """Get all orders (admin only)"""
    try:
        with get_db_context() as db:
            orders = db.query(Order).join(User).order_by(Order.created_at.desc()).all()
            
            result = []
            for order in orders:
                items_count = len(order.items)
                result.append({
                    "id": order.id,
                    "user_id": order.user_id,
                    "username": order.user.username,
                    "total_price": float(order.total_price),
                    "status": order.status,
                    "items_count": items_count,
                    "created_at": order.created_at.isoformat()
                })
            
            return {
                "success": True,
                "count": len(result),
                "orders": result
            }
    except Exception as e:
        logger.error(f"Debug orders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/tables")
async def debug_tables(admin: dict = Depends(verify_admin)):
    """Get all database tables structure (admin only)"""
    try:
        from app.database.connection import engine
        
        inspector = inspect(engine)
        result = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"])
                })
            result[table_name] = columns
        
        return {"success": True, "tables": result}
    except Exception as e:
        logger.error(f"Debug tables error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug/query")
async def debug_query(
    query: str,
    admin: dict = Depends(verify_admin)
):
    """Execute custom SQL query (admin only) - READ ONLY"""
    try:
        # Security: only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries allowed")
        
        with get_db_context() as db:
            result = db.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
        
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        logger.error(f"Debug query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
