from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/auth/login")
def login(user: UserLogin):
    """Simplified login endpoint - integrate with your auth system"""
    if user.username == "admin" and user.password == "admin123":
        return {
            "access_token": "sample_token_123", 
            "token_type": "bearer",
            "message": "Login successful"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/auth/status")
def auth_status():
    """Check authentication status"""
    return {"message": "Auth service is running"}
