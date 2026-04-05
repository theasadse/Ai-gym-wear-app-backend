from typing import Iterable, Set

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.db import get_redis
from app.core.logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple per-IP, per-path fixed-window rate limiter backed by Redis.
    """

    def __init__(
        self,
        app,
        limit: int,
        window_seconds: int,
        exempt_paths: Iterable[str] | None = None,
    ):
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self.exempt_paths: Set[str] = set(exempt_paths or [])

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.exempt_paths or self.limit <= 0:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        key = f"rl:{path}:{ip}"

        try:
            redis = await get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.window)
            if count > self.limit:
                logger.warning(
                    "Rate limit exceeded",
                    extra={"ip": ip, "path": path, "count": count},
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                )
        except Exception as exc:  # fail-open on redis issues
            logger.error("Rate limit middleware error", exc_info=exc)
        return await call_next(request)
