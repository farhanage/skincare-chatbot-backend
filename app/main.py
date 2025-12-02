# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Skincare AI Backend", 
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,
    redirect_slashes=False  
)

# Proxy headers middleware - MUST be first to handle X-Forwarded-* headers from Heroku
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOWED_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Skincare AI Backend is running!",
        "endpoints": {
            "health": "/health",
            "routes": "/routes"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "skin-care-chatbot"}

# Import dan register routers
try:
    # Import routers
    from app.routes.auth import router as auth_router
    from app.routes.products import router as products_router
    from app.routes.admin import router as admin_router
    from app.routes.orders import router as orders_router
    
    # Register dengan prefix /api
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    app.include_router(products_router, prefix="/api/products", tags=["products"])
    app.include_router(admin_router, prefix="/api/debug", tags=["debug"])
    app.include_router(orders_router, prefix="/api/orders", tags=["orders"])
    
except Exception as e:
    logger.error(f" Routes loading failed: {e}")
    raise e

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DOCS_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DOCS_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get(f"/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url=f"/openapi.json", title="docs")

@app.get(f"/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url=f"/openapi.json", title="docs")

@app.get(f"/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)