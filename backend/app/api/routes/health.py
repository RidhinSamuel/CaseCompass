"""Health-check endpoints used by Docker, load balancers, and smoke tests."""
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import engine

log = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, str]:
    """Return 200 if the process is up. Does not touch dependencies."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
def ready() -> JSONResponse:
    """Return 200 only if the database is reachable.

    Load balancers use this to stop routing traffic to an instance that
    cannot serve requests. RabbitMQ is not checked: uploads still succeed
    without it (documents stay `pending`).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        log.warning("Readiness check failed: database unreachable")
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return JSONResponse(status_code=200, content={"status": "ready"})
