import os
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from prisma import Prisma

from app.core.config import settings
from app.core.logger import logger

# Use library engine to avoid spawning a separate port-listening process in restricted environments.
os.environ.setdefault("PRISMA_CLIENT_ENGINE_TYPE", "library")

prisma = Prisma()
_redis: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


@asynccontextmanager
async def lifespan(_app=None):
    logger.info("Connecting to database and cache")
    await prisma.connect()
    await get_redis()
    try:
        yield
    finally:
        logger.info("Disconnecting from database and cache")
        await prisma.disconnect()
        if _redis:
            await _redis.close()
