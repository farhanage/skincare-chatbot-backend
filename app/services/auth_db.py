# app/database/auth_db.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict
from datetime import datetime
import logging
import bcrypt

from app.models.models import User, CartItem
from .connection import get_db_context

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    # bcrypt natively handles passwords, no need for pre-hashing
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_user(username: str, email: str, password: str, full_name: str = "") -> Dict:
    """Create new user"""
    try:
        with get_db_context() as db:
            password_hash = hash_password(password)
            
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role='user'
            )
            
            db.add(new_user)
            db.flush()  # Get the ID before commit
            
            return {
                "success": True,
                "user_id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "full_name": new_user.full_name
            }
    except IntegrityError:
        return {"success": False, "error": "Username atau email sudah terdaftar"}
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return {"success": False, "error": str(e)}

def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if user:
                # Verify password using bcrypt
                password_bytes = password.encode('utf-8')
                stored_hash = user.password_hash.encode('utf-8')
                
                if bcrypt.checkpw(password_bytes, stored_hash):
                    return {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role
                    }
            return None
    except Exception as e:
        logger.error(f"Verify user error: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
            return None
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return None

# Cart functions
def add_to_cart(user_id: int, product_id: str, quantity: int = 1) -> Dict:
    """Add product to cart"""
    try:
        with get_db_context() as db:
            # Check if item already in cart
            existing = db.query(CartItem).filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            ).first()
            
            if existing:
                # Update quantity
                existing.quantity += quantity
            else:
                # Insert new item
                new_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.add(new_item)
            
            return {"success": True, "message": "Produk ditambahkan ke keranjang"}
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        return {"success": False, "error": str(e)}


def get_cart_items(user_id: int) -> list:
    """Get user's cart items"""
    try:
        with get_db_context() as db:
            items = db.query(CartItem).filter(
                CartItem.user_id == user_id
            ).order_by(CartItem.added_at.desc()).all()
            
            return [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "added_at": item.added_at.isoformat()
                }
                for item in items
            ]
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        return []


def update_cart_item(user_id: int, product_id: str, quantity: int) -> Dict:
    """Update cart item quantity"""
    try:
        with get_db_context() as db:
            cart_item = db.query(CartItem).filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            ).first()
            
            if not cart_item:
                return {"success": False, "error": "Item tidak ditemukan di keranjang"}
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                db.delete(cart_item)
            else:
                cart_item.quantity = quantity
            
            return {"success": True, "message": "Keranjang diperbarui"}
    except Exception as e:
        logger.error(f"Update cart error: {e}")
        return {"success": False, "error": str(e)}


def clear_cart(user_id: int) -> Dict:
    """Clear user's cart"""
    try:
        with get_db_context() as db:
            db.query(CartItem).filter(CartItem.user_id == user_id).delete()
            
            return {"success": True, "message": "Keranjang dikosongkan"}
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        return {"success": False, "error": str(e)}