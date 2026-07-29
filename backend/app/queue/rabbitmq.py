"""RabbitMQ producer/consumer glue.

We use `aio-pika` because it plays cleanly with FastAPI's async event loop
and handles connection recovery. The producer publishes ingestion jobs;
workers consume them independently so the API stays responsive under load.
"""
import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from app.core.config import settings

log = logging.getLogger(__name__)


class RabbitMQClient:
    """Thin wrapper around aio-pika providing publish + consume helpers.

    A single instance is created at app startup and shared. `connect()`
    is idempotent and safe to call multiple times.
    """

    def __init__(self, url: str, queue_name: str) -> None:
        self.url = url
        self.queue_name = queue_name
        self._connection: AbstractRobustConnection | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> AbstractRobustConnection:
        """Establish a robust connection with auto-reconnect."""
        async with self._lock:
            if self._connection is None or self._connection.is_closed:
                log.info("Connecting to RabbitMQ at %s", self.url)
                self._connection = await aio_pika.connect_robust(self.url)
        return self._connection

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            log.info("RabbitMQ connection closed")

    async def publish(self, payload: dict[str, Any]) -> None:
        """Publish a durable message to the ingest queue."""
        conn = await self.connect()
        async with conn.channel() as channel:
            # Declare here to be safe on cold starts. Idempotent.
            queue = await channel.declare_queue(self.queue_name, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode("utf-8"),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
                routing_key=queue.name,
            )
            log.debug("Published message to %s: %s", self.queue_name, payload)

    async def consume(
        self,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        prefetch: int = 4,
    ) -> None:
        """Consume messages forever, calling `handler` for each one.

        Prefetch is bounded so a single worker doesn't hoard the queue —
        this lets us scale by simply adding more worker containers.
        """
        conn = await self.connect()
        channel = await conn.channel()
        await channel.set_qos(prefetch_count=prefetch)
        queue = await channel.declare_queue(self.queue_name, durable=True)

        log.info("Worker listening on queue %s (prefetch=%d)", self.queue_name, prefetch)
        async with queue.iterator() as it:
            async for message in it:
                async with message.process(requeue=False):
                    try:
                        payload = json.loads(message.body.decode("utf-8"))
                        await handler(payload)
                    except Exception:  # noqa: BLE001
                        log.exception("Handler failed for message; dropping")


# Module-level singleton used by the FastAPI app + workers.
rabbitmq = RabbitMQClient(
    url=settings.rabbitmq_url,
    queue_name=settings.rabbitmq_ingest_queue,
)
