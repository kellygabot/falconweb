from motor.motor_asyncio import AsyncClient, AsyncDatabase

from app.core.config import settings

_mongo_client: AsyncClient = None
_mongo_db: AsyncDatabase = None


async def connect_mongo():
    global _mongo_client, _mongo_db
    _mongo_client = AsyncClient(settings.mongodb_url)
    _mongo_db = _mongo_client.falconweb


async def disconnect_mongo():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()


def get_mongo_db() -> AsyncDatabase:
    return _mongo_db
