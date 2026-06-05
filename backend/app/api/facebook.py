from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncDatabase

from app.db.mongo import get_mongo_db

router = APIRouter()


@router.get("/posts")
async def get_cached_posts(mongo_db: AsyncDatabase = Depends(get_mongo_db)):
    # TODO: Return cached Facebook posts from both pages
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/refresh")
async def refresh_facebook_feed(mongo_db: AsyncDatabase = Depends(get_mongo_db)):
    # TODO: Manually trigger refresh of Facebook feed from both pages
    # Normally runs on background job (hourly)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
