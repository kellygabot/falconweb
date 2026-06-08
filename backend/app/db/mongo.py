from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

_mongo_client: AsyncIOMotorClient = None
_mongo_db = None


async def connect_mongo():
    global _mongo_client, _mongo_db
    _mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    _mongo_db = _mongo_client.falconweb


async def disconnect_mongo():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()


def get_mongo_db():
    return _mongo_db
