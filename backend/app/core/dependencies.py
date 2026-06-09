from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.postgres import get_db
from app.models.user import User


async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate JWT token from Authorization header.
    Returns the current authenticated user.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No user ID in token")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


def has_role(required_roles: list[str]):
    """
    Check if the current user has any of the required roles.
    Usage: @router.get("/admin", dependencies=[Depends(has_role(["super_admin", "school_admin"]))])
    """
    async def check_role(
        user: User = Depends(get_current_user),
    ) -> User:
        user_roles = [r.name for r in user.roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_roles)}"
            )
        return user

    return check_role
