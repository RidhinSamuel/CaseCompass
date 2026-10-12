"""FastAPI application entrypoint.

Wires up: CORS, logging, health checks, auth, documents, and search routes.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, documents, health, search
from app.core.config import settings
from app.core.logging import setup_logging
from app.queue.rabbitmq import rabbitmq

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan: init logging + open RabbitMQ connection on startup."""
    setup_logging(settings.log_level)
    try:
        # Warm the RabbitMQ connection so first publish is fast.
        await rabbitmq.connect()
    except Exception:  # noqa: BLE001
        # Don't crash the API if the broker is briefly unavailable;
        # publish() will lazily reconnect.
        log.warning("RabbitMQ unavailable at startup; will retry on first publish")
    yield
    await rabbitmq.close()


def create_app() -> FastAPI:
    # Interactive API docs are disabled in production to reduce attack surface.
    docs_enabled = not settings.is_production
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Judicial RAG platform with hybrid search and user-scoped retrieval.",
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the full traceback server-side; never leak internals to clients.
        log.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    return app


app = create_app()
