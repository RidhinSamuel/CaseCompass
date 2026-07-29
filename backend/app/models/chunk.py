"""DocumentChunk — a chunked, embedded piece of a document.

Every chunk carries user_id and case_id so hybrid retrieval can filter
by user before doing vector similarity. This is the enforcement point
for per-user isolation.
"""
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base, TimestampMixin


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Denormalized user_id / case_id for fast metadata-filtered retrieval.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    case_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.embedding_dim), nullable=False
    )
    chunk_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        # Composite index accelerates user-scoped retrieval.
        Index("ix_chunks_user_case", "user_id", "case_id"),
    )
