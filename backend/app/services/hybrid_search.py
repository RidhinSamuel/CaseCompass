"""Hybrid search: vector similarity + full-text keyword scoring.

Isolation contract:
    Every query MUST include `user_id`. The SQL filter enforces this at
    the database level, so no vector-similarity result can leak across
    user boundaries.

Ranking:
    We fetch the top-N by vector cosine distance and the top-N by
    Postgres ts_rank, then combine them with a weighted sum
    (alpha * vector_score + (1-alpha) * bm25_score).
"""
import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.core.config import settings

log = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    score: float
    case_id: str | None
    chunk_index: int


def hybrid_search(
    db: Session,
    *,
    user_id: uuid.UUID,
    query_text: str,
    query_embedding: list[float],
    case_id: str | None = None,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """Run hybrid retrieval scoped to a single user.

    Returns the top_k merged results ranked by combined score.
    """
    # pgvector uses `<=>` for cosine distance (smaller is closer),
    # so we convert to a similarity in [0, 1].
    sql = text(
        """
        WITH vec AS (
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.content,
                c.chunk_index,
                c.case_id,
                d.title AS document_title,
                1 - (c.embedding <=> CAST(:qvec AS vector)) AS vec_score
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.user_id = :user_id
              AND (:case_id IS NULL OR c.case_id = :case_id)
            ORDER BY c.embedding <=> CAST(:qvec AS vector)
            LIMIT :vec_k
        ),
        kw AS (
            SELECT
                c.id AS chunk_id,
                ts_rank_cd(
                    to_tsvector('english', c.content),
                    plainto_tsquery('english', :qtext)
                ) AS kw_score
            FROM document_chunks c
            WHERE c.user_id = :user_id
              AND (:case_id IS NULL OR c.case_id = :case_id)
              AND to_tsvector('english', c.content) @@ plainto_tsquery('english', :qtext)
            ORDER BY kw_score DESC
            LIMIT :vec_k
        )
        SELECT
            v.chunk_id,
            v.document_id,
            v.document_title,
            v.content,
            v.case_id,
            v.chunk_index,
            (:alpha * v.vec_score) + ((1 - :alpha) * COALESCE(kw.kw_score, 0)) AS score
        FROM vec v
        LEFT JOIN kw ON kw.chunk_id = v.chunk_id
        ORDER BY score DESC
        LIMIT :top_k;
        """
    ).bindparams(
        bindparam("qvec"),
        bindparam("qtext"),
        bindparam("user_id"),
        bindparam("case_id"),
        bindparam("vec_k"),
        bindparam("alpha"),
        bindparam("top_k"),
    )

    rows = db.execute(
        sql,
        {
            "qvec": query_embedding,
            "qtext": query_text,
            "user_id": user_id,
            "case_id": case_id,
            "vec_k": settings.top_k_vector,
            "alpha": settings.hybrid_alpha,
            "top_k": top_k,
        },
    ).mappings().all()

    log.debug("Hybrid search: user=%s returned %d chunks", user_id, len(rows))
    return [
        RetrievedChunk(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            document_title=r["document_title"],
            content=r["content"],
            score=float(r["score"]),
            case_id=r["case_id"],
            chunk_index=r["chunk_index"],
        )
        for r in rows
    ]
