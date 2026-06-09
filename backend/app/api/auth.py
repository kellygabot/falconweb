from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    roles: list[str]

    class Config:
        from_attributes = True


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(
        {"sub": user.id, "email": user.email},
        remember_me=request.remember_me
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Refresh an access token using a valid refresh token.
    Request body: { "refresh_token": "token_string" }
    """
    if not request or "refresh_token" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required"
        )

    try:
        payload = decode_token(request["refresh_token"])
        user_id = payload.get("sub")

        if not user_id or payload.get("type") != "refresh":
            raise ValueError("Invalid or expired refresh token")

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token({"sub": user.id, "email": user.email})
        new_refresh_token = create_refresh_token({"sub": user.id, "email": user.email})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Requires: Authorization header with Bearer token
    """
    return UserInfo(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        roles=[r.name for r in user.roles]
    )
