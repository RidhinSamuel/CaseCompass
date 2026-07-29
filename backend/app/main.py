"""FastAPI application entrypoint.

Wires up: CORS, logging, health checks, auth, documents, and search routes.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, documents, health, search
from app.core.config import settings
from app.core.logging import setup_logging
from app.queue.rabbitmq import rabbitmq


@asynccontextmanager
async def lifespan(_: FastAPI):
    """App lifespan: init logging + open RabbitMQ connection on startup."""
    setup_logging()
    try:
        # Warm the RabbitMQ connection so first publish is fast.
        await rabbitmq.connect()
    except Exception:  # noqa: BLE001
        # Don't crash the API if the broker is briefly unavailable;
        # publish() will lazily reconnect.
        pass
    yield
    await rabbitmq.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Judicial RAG platform with hybrid search and user-scoped retrieval.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    return app


app = create_app()
