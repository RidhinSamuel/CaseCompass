"""Health-check endpoints used by Docker, load balancers, and smoke tests."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, str]:
    """Return 200 if the process is up."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
def ready() -> dict[str, str]:
    """Return 200 if the app is ready to serve traffic.

    We keep this shallow on purpose. Deep readiness (DB, RabbitMQ, Redis)
    is exposed by orchestrators via other tooling if desired.
    """
    return {"status": "ready"}
