# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Initialize database (jika ada)
        try:
            from app.database.connection import init_db
            init_db()
            logger.info(" Database initialized")
        except ImportError:
            logger.info("ℹ No database configured")
        
        # Skip pre-loading AI model for faster startup
        # Model will be lazy-loaded on first prediction request
        logger.info("ℹ AI model will be loaded on first use (lazy loading)")
        
    except Exception as e:
        logger.error(f" Startup error: {e}")
    
    yield
    # Shutdown would go here

app = FastAPI(
    title="Skin Care ChatBot API", 
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Skin Care ChatBot API is running!",
        "endpoints": {
            "health": "/health",
            "predict": ["/predict", "/api/v1/predict"],
            "chat": ["/chat", "/api/v1/chat"],
            "routes": "/routes"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "skin-care-chatbot"}

# Import dan register routers
try:
    # Import routers
    from app.routes.predict import router as predict_router
    from app.routes.chat import router as chat_router
    from app.routes.auth import router as auth_router
    from app.routes.products import router as products_router
    from app.routes.admin import router as admin_router
    from app.routes.orders import router as orders_router
    
    # Register dengan prefix API v1
    app.include_router(predict_router, prefix="/api/v1", tags=["prediction"])
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(products_router, prefix="/api/v1", tags=["products"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
    
    # Juga register tanpa prefix untuk compatibility
    app.include_router(predict_router, tags=["prediction-legacy"])
    app.include_router(chat_router, tags=["chat-legacy"])
    
    logger.info(" All routes loaded successfully")
    logger.info(" Available endpoints:")
    logger.info("   - POST /api/v1/predict")
    logger.info("   - POST /predict") 
    logger.info("   - POST /api/v1/chat")
    logger.info("   - POST /chat")
    logger.info("   - POST /api/v1/auth/register")
    logger.info("   - POST /api/v1/auth/login")
    logger.info("   - GET  /api/v1/products")
    logger.info("   - POST /api/v1/cart/add")
    logger.info("   - GET  /api/v1/cart")
    logger.info("   - GET  /api/v1/admin/debug/* (Admin Only)")
    
except Exception as e:
    logger.error(f" Routes loading failed: {e}")
    raise e

# Debug endpoint untuk melihat semua routes
@app.get("/routes")
async def list_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods)
            })
    return routes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)