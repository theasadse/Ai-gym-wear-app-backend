import json
from typing import Optional, Sequence, List

from app.api.schemas import ProductOut
from app.core.logger import logger
from app.db import prisma, get_redis

PRODUCT_CACHE_TTL = 60  # seconds


def _cache_key(prefix: str, **kwargs) -> str:
    parts = [prefix] + [f"{k}={v}" for k, v in sorted(kwargs.items()) if v]
    return "|".join(parts) or prefix


async def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    size: Optional[str] = None,
    max_price: Optional[float] = None,
) -> Sequence[ProductOut]:
    cache_key = _cache_key(
        "products", search=search, category=category, tag=tag, size=size, max_price=max_price
    )
    redis = await get_redis()

    cached = await redis.get(cache_key)
    if cached:
        logger.info("Products cache hit", extra={"key": cache_key})
        data = json.loads(cached)
        return [ProductOut(**item) for item in data]

    logger.info("Products cache miss", extra={"key": cache_key})
    where = {}
    if category:
        where["category"] = category
    if tag:
        where["tags"] = {"has": tag}
    if search:
        where["OR"] = [
            {"name": {"contains": search, "mode": "insensitive"}},
            {"tags": {"has": search}},
        ]
    if size:
        where["sizes"] = {"contains": size}
    if max_price is not None:
        where["price"] = {"lte": max_price}

    products = await prisma.product.find_many(where=where or None, order={"createdAt": "desc"})

    serialized = [
        ProductOut.model_validate(p, from_attributes=True).model_dump()
        for p in products
    ]
    await redis.set(cache_key, json.dumps(serialized), ex=PRODUCT_CACHE_TTL)
    return [ProductOut(**item) for item in serialized]


async def list_recommendations(user_id: Optional[str] = None) -> List[ProductOut]:
    """
    Return featured/new arrivals fallback. Personalization hook via user_id (unused).
    """
    cache_key = _cache_key("recs", user=user_id or "anon")
    redis = await get_redis()

    cached = await redis.get(cache_key)
    if cached:
        logger.info("Recommendations cache hit", extra={"key": cache_key})
        data = json.loads(cached)
        return [ProductOut(**item) for item in data]

    where = {"OR": [{"featured": True}, {"newArrival": True}]}
    products = await prisma.product.find_many(where=where, order={"createdAt": "desc"}, take=12)

    serialized = [
        ProductOut.model_validate(p, from_attributes=True).model_dump()
        for p in products
    ]
    await redis.set(cache_key, json.dumps(serialized), ex=PRODUCT_CACHE_TTL)
    return [ProductOut(**item) for item in serialized]
