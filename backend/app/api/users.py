from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.postgres import get_db

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    roles: list[str]  # ["student", "advisor"]


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    roles: list[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # TODO: Super admin creates user account
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    # TODO: Get user profile
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
