"""Application configuration loaded from environment variables.

All secrets and environment-specific values live here. Never hard-code
credentials in source. Use `.env` for local dev; the file is git-ignored.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object. Values are read from env vars and `.env`."""

    # --- App ---
    app_name: str = "Case Compass"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    # --- Database (Postgres + pgvector) ---
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/case_compass",
        alias="DATABASE_URL",
    )

    # --- Redis ---
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # --- RabbitMQ ---
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/", alias="RABBITMQ_URL"
    )
    rabbitmq_ingest_queue: str = Field(
        default="case_compass.ingest", alias="RABBITMQ_INGEST_QUEUE"
    )

    # --- Hugging Face / RAG ---
    hf_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="HF_EMBEDDING_MODEL"
    )
    hf_llm_model: str = Field(
        default="google/flan-t5-base", alias="HF_LLM_MODEL"
    )
    huggingface_api_token: str | None = Field(default=None, alias="HUGGINGFACE_API_TOKEN")
    embedding_dim: int = Field(default=384, alias="EMBEDDING_DIM")

    # --- Retrieval tuning ---
    top_k_vector: int = Field(default=10, alias="TOP_K_VECTOR")
    top_k_final: int = Field(default=5, alias="TOP_K_FINAL")
    hybrid_alpha: float = Field(
        default=0.6, alias="HYBRID_ALPHA",
        description="Weight for vector score vs BM25 in hybrid ranking (0..1)",
    )

    # --- Auth ---
    jwt_secret_key: str = Field(default="change-me-in-prod", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60 * 24, alias="JWT_EXPIRE_MINUTES")

    # --- CORS ---
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()


settings = get_settings()
