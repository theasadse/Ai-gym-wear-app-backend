from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router, public_router
from app.db import lifespan
from app.core.config import settings


tags_metadata = [
    {
        "name": "health",
        "description": "Liveness and readiness checks.",
    },
    {
        "name": "products",
        "description": "Product catalogue endpoints for the storefront grid.",
    },
    {
        "name": "ai",
        "description": "AI stylist chat endpoints.",
    },
]

app = FastAPI(
    title="Gym Wear Backend",
    description="FastAPI backend for gym-wear storefront with product catalogue, AI chat, Postgres, and Redis caching.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")
app.include_router(public_router)
