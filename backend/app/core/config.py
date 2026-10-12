"""Application configuration loaded from environment variables.

All secrets and environment-specific values live here. Never hard-code
credentials in source. Use `.env` for local dev; the file is git-ignored.
"""
import json
from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Placeholder secrets that must never be used in production.
_INSECURE_SECRETS = {
    "change-me-in-prod",
    "docker-dev-secret-key-change-me",
    "test-secret",
    "ci-secret",
}


class Settings(BaseSettings):
    """Central settings object. Values are read from env vars and `.env`."""

    # --- App ---
    app_name: str = "Case Compass"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Database (Postgres + pgvector) ---
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/case_compass",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")

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
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        alias="GEMINI_BASE_URL",
    )
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")
    embedding_dim: int = Field(default=384, alias="EMBEDDING_DIM")

    # --- Retrieval tuning ---
    top_k_vector: int = Field(default=10, alias="TOP_K_VECTOR")
    top_k_final: int = Field(default=5, alias="TOP_K_FINAL")
    hybrid_alpha: float = Field(
        default=0.6, alias="HYBRID_ALPHA", ge=0, le=1,
        description="Weight for vector score vs BM25 in hybrid ranking (0..1)",
    )

    # --- Auth ---
    jwt_secret_key: str = Field(default="change-me-in-prod", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60 * 24, alias="JWT_EXPIRE_MINUTES")

    # --- CORS ---
    # Accepts a JSON list or a comma-separated string, e.g.
    # CORS_ORIGINS=https://app.example.com,https://www.example.com
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    @model_validator(mode="after")
    def _check_production_safety(self) -> "Settings":
        """Fail fast on insecure configuration when running in production."""
        if not self.is_production:
            return self
        problems: list[str] = []
        if self.jwt_secret_key in _INSECURE_SECRETS or len(self.jwt_secret_key) < 32:
            problems.append("JWT_SECRET_KEY must be a random string of at least 32 characters")
        if self.debug:
            problems.append("DEBUG must be false")
        if "*" in self.cors_origins:
            problems.append("CORS_ORIGINS must list explicit origins, not '*'")
        if problems:
            raise ValueError("Unsafe production configuration: " + "; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()


settings = get_settings()
