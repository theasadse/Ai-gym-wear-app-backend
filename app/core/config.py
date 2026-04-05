from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = Field(
        "distilgpt2",
        description="HF model id; default uses a small CPU-friendly model.",
    )
    device_map_auto: bool = Field(
        False,
        description="Enable transformers device_map='auto' for GPU if available.",
    )
    max_tokens: int = Field(
        120,
        description="Maximum tokens to generate per reply.",
    )
    database_url: str = Field(
        "postgresql://postgres:postgres@localhost:5432/gymwear",
        description="PostgreSQL connection string.",
    )
    redis_url: str = Field(
        "redis://localhost:6379/0",
        description="Redis connection string for caching.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
