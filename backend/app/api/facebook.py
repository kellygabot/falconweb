from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import httpx
import logging

from app.db.mongo import get_mongo_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


async def fetch_page_posts(page_token: str, page_name: str) -> list[dict]:
    """
    Fetch posts from a Facebook page using Graph API.
    Returns list of post objects with message, image, created_time, permalink_url.
    """
    url = "https://graph.facebook.com/v20.0/me/posts"
    params = {
        "fields": "message,picture,created_time,permalink_url,likes.limit(0).summary(1)",
        "access_token": page_token,
        "limit": 10,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            posts = []
            for item in data.get("data", []):
                posts.append({
                    "message": item.get("message", ""),
                    "image": item.get("picture"),
                    "created_time": item.get("created_time"),
                    "url": item.get("permalink_url"),
                    "likes": item.get("likes", {}).get("summary", {}).get("total_count", 0),
                    "source": page_name,
                })

            return posts

    except httpx.RequestError as e:
        logger.error(f"Failed to fetch posts from {page_name}: {str(e)}")
        return []


@router.get("/posts")
async def get_cached_posts(mongo_db = Depends(get_mongo_db)):
    """
    Return cached Facebook posts from both pages.
    """
    try:
        posts = await mongo_db.facebook_posts.find(
            {"cached": True}
        ).sort("created_time", -1).limit(20).to_list(None)

        return {
            "posts": posts,
            "count": len(posts),
            "last_refreshed": posts[0].get("last_refreshed") if posts else None,
        }
    except Exception as e:
        logger.error(f"Error fetching cached posts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch posts"
        )


@router.post("/refresh")
async def refresh_facebook_feed(mongo_db = Depends(get_mongo_db)):
    """
    Manually trigger refresh of Facebook feed from both pages.
    Normally runs on background job (hourly).
    """
    if not settings.facebook_page_token_1 or not settings.facebook_page_token_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facebook tokens not configured"
        )

    try:
        # Fetch from both pages
        posts_page1 = await fetch_page_posts(
            settings.facebook_page_token_1,
            "Falcon School"
        )
        posts_page2 = await fetch_page_posts(
            settings.facebook_page_token_2,
            "Falcon School News"
        )

        # Clear old cache
        await mongo_db.facebook_posts.delete_many({"cached": True})

        # Insert new posts
        all_posts = posts_page1 + posts_page2
        if all_posts:
            for post in all_posts:
                post["cached"] = True
                post["last_refreshed"] = datetime.utcnow()

            await mongo_db.facebook_posts.insert_many(all_posts)

        return {
            "status": "refreshed",
            "posts_from_page1": len(posts_page1),
            "posts_from_page2": len(posts_page2),
            "total": len(all_posts),
        }

    except Exception as e:
        logger.error(f"Error refreshing Facebook feed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh feed"
        )
