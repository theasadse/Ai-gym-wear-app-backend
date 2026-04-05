from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

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
        "postgresql://postgres:postgres@localhost:5442/gymwear",
        description="PostgreSQL connection string.",
    )
    redis_url: str = Field(
        "redis://localhost:6380/0",
        description="Redis connection string for caching.",
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins list.",
    )
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key; when set, Gemini is used instead of local HF model.",
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash-latest",
        description="Gemini model to use when gemini_api_key is provided (e.g., gemini-1.5-flash-latest).",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
