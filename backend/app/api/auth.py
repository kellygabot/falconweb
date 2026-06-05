from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # TODO: Implement login logic
    # 1. Find user by email
    # 2. Verify password
    # 3. Generate access + refresh tokens
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    # TODO: Implement token refresh logic
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
