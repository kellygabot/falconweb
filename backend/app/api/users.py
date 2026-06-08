from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.postgres import get_db
from app.core.security import hash_password
from app.models.user import User, Role

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    roles: list[str]  # ["student", "advisor", "instructor", etc]


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    roles: list[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hash_password(user.password),
        is_active=True,
    )

    # Assign roles
    for role_name in user.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            # Create role if it doesn't exist
            role = Role(name=role_name, description=f"{role_name} role")
            db.add(role)
        new_user.roles.append(role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        is_active=new_user.is_active,
        roles=[r.name for r in new_user.roles]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        roles=[r.name for r in user.roles]
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, update: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if "first_name" in update:
        user.first_name = update["first_name"]
    if "last_name" in update:
        user.last_name = update["last_name"]
    if "is_active" in update:
        user.is_active = update["is_active"]

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        roles=[r.name for r in user.roles]
    )
