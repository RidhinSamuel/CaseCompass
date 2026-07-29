"""Ingestion worker.

Runs as its own process (or as many replicas as you want). Consumes
ingestion events from RabbitMQ, chunks + embeds the document, and writes
chunks to Postgres with the owner's user_id/case_id so retrieval is
user-scoped by construction.

Start locally:
    uv run python -m app.workers.ingest_worker
"""
import asyncio
import logging
import uuid
from typing import Any

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.queue.rabbitmq import rabbitmq
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts

log = logging.getLogger(__name__)


def _process_document(document_id: uuid.UUID) -> None:
    """Chunk + embed a single document, write chunks in one transaction."""
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if doc is None:
            log.warning("Document %s not found (deleted?), skipping", document_id)
            return

        try:
            doc.status = "processing"
            db.commit()

            chunks = chunk_text(doc.raw_text)
            if not chunks:
                doc.status = "ready"
                doc.chunk_count = 0
                db.commit()
                return

            vectors = embed_texts(chunks)
            db.bulk_save_objects(
                [
                    DocumentChunk(
                        document_id=doc.id,
                        user_id=doc.user_id,   # propagate ownership onto every chunk
                        case_id=doc.case_id,
                        chunk_index=i,
                        content=text,
                        embedding=vec,
                        chunk_metadata={
                            "case_id": doc.case_id,
                            "source_filename": doc.source_filename,
                        },
                    )
                    for i, (text, vec) in enumerate(zip(chunks, vectors, strict=True))
                ]
            )
            doc.chunk_count = len(chunks)
            doc.status = "ready"
            db.commit()
            log.info("Ingested document %s: %d chunks", document_id, len(chunks))
        except Exception:  # noqa: BLE001
            db.rollback()
            log.exception("Ingestion failed for document %s", document_id)
            with SessionLocal() as db2:
                d = db2.get(Document, document_id)
                if d is not None:
                    d.status = "failed"
                    db2.commit()


async def _handle_message(payload: dict[str, Any]) -> None:
    """RabbitMQ message handler dispatched by the queue consumer."""
    doc_id_raw = payload.get("document_id")
    if not doc_id_raw:
        log.warning("Ingest event missing document_id: %s", payload)
        return
    doc_id = uuid.UUID(doc_id_raw)
    # Run the sync DB/embedding work in a thread so we don't block the loop.
    await asyncio.to_thread(_process_document, doc_id)


async def main() -> None:
    setup_logging()
    log.info("Starting Case Compass ingest worker")
    await rabbitmq.consume(_handle_message, prefetch=4)


if __name__ == "__main__":
    asyncio.run(main())
