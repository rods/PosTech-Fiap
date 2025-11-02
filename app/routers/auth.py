from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.auth import authenticate_user, create_access_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Authentication"],
)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    message: str

@router.post("/auth/login", response_model=Token)
def login(user: UserLogin):
    """
    AAutentica o usuario e retorna JWT access token.
    
    For testing purposes, you can use:
    - username: "admin"
    - password: "admin123"
    """
    # Authenticate user
    authenticated_user = authenticate_user(user.username, user.password)
    if not authenticated_user:
        logger.warning(f"Failed login attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Successful login for user: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }

@router.get("/auth/status")
def auth_status():
    """Check authentication status"""
    return {"message": "Auth service is running"}
