# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
from datetime import datetime, timedelta
import logging

from app.database.auth_db import create_user, verify_user, get_user_by_id

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production-2024"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = ""

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user: Optional[dict] = None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    try:
        # Validate input
        if len(request.password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password harus minimal 6 karakter"
            )
        
        # Create user
        result = create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Create token
        access_token = create_access_token(
            data={"user_id": result["user_id"], "username": result["username"]}
        )
        
        return AuthResponse(
            success=True,
            message="Registrasi berhasil!",
            access_token=access_token,
            token_type="bearer",
            user={
                "id": result["user_id"],
                "username": result["username"],
                "email": result["email"],
                "full_name": result["full_name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """User login - accepts form data"""
    try:
        user = verify_user(username, password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Username atau password salah"
            )
        
        # Create token
        access_token = create_access_token(
            data={"user_id": user["id"], "username": user["username"], "role": user.get("role", "user")}
        )
        
        return {
            "success": True,
            "message": "Login berhasil!",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "role": user.get("role", "user")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user info"""
    return {
        "success": True,
        "user": current_user
    }
