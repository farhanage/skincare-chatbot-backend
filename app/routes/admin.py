# app/routes/admin.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.routes.auth import verify_token
from app.database.auth_db import get_user_by_id
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Database paths
DB_DIR = Path(__file__).parent.parent.parent
USERS_DB = DB_DIR / "users.db"
PRODUCTS_DB = DB_DIR / "database.db"

def verify_admin(current_user: dict = Depends(verify_token)) -> dict:
    """Verify if user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/debug/info")
async def debug_info(admin: dict = Depends(verify_admin)):
    """Get system debug information"""
    try:
        info = {
            "timestamp": datetime.now().isoformat(),
            "admin_user": admin["username"],
            "databases": {
                "users_db": str(USERS_DB),
                "products_db": str(PRODUCTS_DB),
                "users_exists": USERS_DB.exists(),
                "products_exists": PRODUCTS_DB.exists()
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
        conn = sqlite3.connect(str(USERS_DB), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "role": row[4],
                "created_at": row[5]
            })
        
        conn.close()
        return {"success": True, "count": len(users), "users": users}
    except Exception as e:
        logger.error(f"Debug users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/products")
async def debug_products(admin: dict = Depends(verify_admin)):
    """Get all products from database (admin only)"""
    try:
        conn = sqlite3.connect(str(PRODUCTS_DB), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, description, price, category FROM products')
        
        products = []
        for row in cursor.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3],
                "category": row[4]
            })
        
        conn.close()
        return {"success": True, "count": len(products), "products": products}
    except Exception as e:
        logger.error(f"Debug products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/carts")
async def debug_carts(admin: dict = Depends(verify_admin)):
    """Get all cart items (admin only)"""
    try:
        conn = sqlite3.connect(str(USERS_DB), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.user_id, u.username, c.product_id, c.quantity, c.added_at
            FROM cart_items c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.added_at DESC
        ''')
        
        carts = []
        for row in cursor.fetchall():
            carts.append({
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "product_id": row[3],
                "quantity": row[4],
                "added_at": row[5]
            })
        
        conn.close()
        return {"success": True, "count": len(carts), "carts": carts}
    except Exception as e:
        logger.error(f"Debug carts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/tables")
async def debug_tables(admin: dict = Depends(verify_admin)):
    """Get all database tables structure (admin only)"""
    try:
        result = {"users_db": {}, "products_db": {}}
        
        # Users DB tables
        conn = sqlite3.connect(str(USERS_DB), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
            result["users_db"][table] = columns
        
        conn.close()
        
        # Products DB tables
        conn = sqlite3.connect(str(PRODUCTS_DB), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
            result["products_db"][table] = columns
        
        conn.close()
        
        return {"success": True, "tables": result}
    except Exception as e:
        logger.error(f"Debug tables error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/query")
async def debug_query(
    db: str,  # "users" or "products"
    query: str,
    admin: dict = Depends(verify_admin)
):
    """Execute custom SQL query (admin only) - READ ONLY"""
    try:
        # Security: only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries allowed")
        
        db_path = USERS_DB if db == "users" else PRODUCTS_DB
        
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        conn.close()
        
        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error(f"Debug query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
