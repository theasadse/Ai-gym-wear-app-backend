from fastapi import FastAPI

from app.api.routes import router as api_router
from app.db import lifespan


app = FastAPI(title="Gym Wear Backend", version="0.1.0", lifespan=lifespan)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")
