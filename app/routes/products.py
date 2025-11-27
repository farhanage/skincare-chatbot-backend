# app/routes/products.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.database.products_data import PRODUCTS
from app.database.auth_db import add_to_cart, get_cart_items, update_cart_item, clear_cart
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

@router.get("/products", response_model=ProductResponse)
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all products with optional filtering"""
    try:
        filtered_products = PRODUCTS
        
        # Filter by category
        if category:
            filtered_products = [
                p for p in filtered_products
                if p["category"].lower() == category.lower()
            ]
        
        # Search by name or description
        if search:
            search_lower = search.lower()
            filtered_products = [
                p for p in filtered_products
                if search_lower in p["name"].lower() or search_lower in p["description"].lower()
            ]
        
        return ProductResponse(
            success=True,
            products=filtered_products,
            total=len(filtered_products)
        )
        
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    try:
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        return {
            "success": True,
            "product": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cart/add")
async def add_product_to_cart(
    request: AddToCartRequest,
    current_user: dict = Depends(verify_token)
):
    """Add product to cart (requires authentication)"""
    try:
        # Verify product exists
        product = next((p for p in PRODUCTS if p["id"] == request.product_id), None)
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
async def get_cart(current_user: dict = Depends(verify_token)):
    """Get user's cart"""
    try:
        cart_items = get_cart_items(current_user["id"])
        
        # Enrich with product details
        enriched_items = []
        total_price = 0.0
        total_items = 0
        
        for item in cart_items:
            product = next((p for p in PRODUCTS if p["id"] == item["product_id"]), None)
            if product:
                item_total = product["price"] * item["quantity"]
                enriched_items.append({
                    **item,
                    "product": product,
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

@router.put("/cart/update")
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

@router.delete("/cart/clear")
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
async def checkout(current_user: dict = Depends(verify_token)):
    """Checkout (simplified - just clears cart)"""
    try:
        cart_items = get_cart_items(current_user["id"])
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Keranjang kosong")
        
        # Calculate total
        total_price = 0.0
        for item in cart_items:
            product = next((p for p in PRODUCTS if p["id"] == item["product_id"]), None)
            if product:
                total_price += product["price"] * item["quantity"]
        
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

from datetime import datetime
