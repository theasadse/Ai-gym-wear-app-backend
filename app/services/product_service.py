import json
from typing import Optional, Sequence

from prisma.models import Product

from app.api.schemas import ProductOut
from app.core.logger import logger
from app.db import prisma, get_redis

PRODUCT_CACHE_TTL = 60  # seconds


async def list_products(category: Optional[str] = None) -> Sequence[ProductOut]:
    """
    Fetch products with optional category filter, cached in Redis.
    """
    cache_key = f"products:{category or 'all'}"
    redis = await get_redis()

    cached = await redis.get(cache_key)
    if cached:
        logger.info("Products cache hit", extra={"category": category})
        data = json.loads(cached)
        return [ProductOut(**item) for item in data]

    logger.info("Products cache miss", extra={"category": category})
    products = await prisma.product.find_many(
        where={"category": category} if category else None,
        order={"createdAt": "desc"},
    )

    serialized = [
        ProductOut.model_validate(p, from_attributes=True).model_dump()
        for p in products
    ]
    await redis.set(cache_key, json.dumps(serialized), ex=PRODUCT_CACHE_TTL)
    return [ProductOut(**item) for item in serialized]
