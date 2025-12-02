# app/routes/products.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.auth_db import add_to_cart, get_cart_items, update_cart_item, clear_cart
from app.services.connection import get_db
from app.models.models import Product
from app.routes.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = 1

class UpdateCartRequest(BaseModel):
    product_id: str
    quantity: int

class ProductResponse(BaseModel):
    success: bool
    products: List[dict]
    total: int

class CartResponse(BaseModel):
    success: bool
    items: List[dict]
    total_items: int
    total_price: float

@router.get("/", response_model=ProductResponse)
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    try:
        # Start with base query
        query = db.query(Product)
        
        # Filter by category
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        # Search by name or description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) | 
                (Product.description.ilike(search_term))
            )
        
        # Execute query
        products = query.all()
        
        # Convert to dict
        filtered_products = [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description or "",
                "price": float(p.price) if p.price else 0,
                "category": p.category or "",
                "image_url": p.image_url or "",
                "for_conditions": p.for_conditions or [],
                "ingredients": p.ingredients or "",
                "usage": p.usage or ""
            }
            for p in products
        ]
        
        return ProductResponse(
            success=True,
            products=filtered_products,
            total=len(filtered_products)
        )
        
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_to_cart")
async def add_product_to_cart(
    request: AddToCartRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Add product to cart (requires authentication)"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == int(request.product_id)).first()
        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        # Add to cart
        result = add_to_cart(
            user_id=current_user["id"],
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cart", response_model=CartResponse)
async def get_cart(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user's cart"""
    try:
        cart_items = get_cart_items(current_user["id"])
        
        # Enrich with product details
        enriched_items = []
        total_price = 0.0
        total_items = 0
        
        for item in cart_items:
            logger.debug(f"Cart item: {item}")
            product = db.query(Product).filter(Product.id == int(item["product_id"])).first()
            if product:
                product_dict = {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description or "",
                    "price": float(product.price) if product.price else 0,
                    "category": product.category or "",
                    "image_url": product.image_url or ""
                }
                item_total = product_dict["price"] * item["quantity"]
                enriched_items.append({
                    **item,
                    "product": product_dict,
                    "item_total": item_total
                })
                total_price += item_total
                total_items += item["quantity"]
        
        return CartResponse(
            success=True,
            items=enriched_items,
            total_items=total_items,
            total_price=total_price
        )
        
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update_cart")
async def update_cart(
    request: UpdateCartRequest,
    current_user: dict = Depends(verify_token)
):
    """Update cart item quantity"""
    try:
        result = update_cart_item(
            user_id=current_user["id"],
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear_cart")
async def clear_user_cart(current_user: dict = Depends(verify_token)):
    """Clear user's cart"""
    try:
        result = clear_cart(current_user["id"])
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout")
async def checkout(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Checkout (simplified - just clears cart)"""
    try:
        cart_items = get_cart_items(current_user["id"])
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Keranjang kosong")
        
        # Calculate total
        total_price = 0.0
        for item in cart_items:
            product = db.query(Product).filter(Product.id == int(item["product_id"])).first()
            if product:
                total_price += float(product.price) * item["quantity"]
        
        # Clear cart (in real app, create order record first)
        clear_cart(current_user["id"])
        
        return {
            "success": True,
            "message": "Checkout berhasil! Terima kasih atas pembelian Anda.",
            "total_price": total_price,
            "order_id": f"ORDER-{current_user['id']}-{int(datetime.now().timestamp())}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get single product by ID"""
    try:
        product = db.query(Product).filter(Product.id == int(product_id)).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        return {
            "success": True,
            "product": {
                "id": str(product.id),
                "name": product.name,
                "description": product.description or "",
                "price": float(product.price) if product.price else 0,
                "category": product.category or "",
                "image_url": product.image_url or "",
                "for_conditions": product.for_conditions or [],
                "ingredients": product.ingredients or "",
                "usage": product.usage or ""
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
