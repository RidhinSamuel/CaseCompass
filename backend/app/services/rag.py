"""RAG orchestrator — glues embeddings, hybrid search, and an LLM together.

The LLM is Google Gemini, called through its OpenAI-compatible API.
Requires `GEMINI_API_KEY`.
"""
import logging
import uuid
from functools import lru_cache

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.document import SearchHit, SearchResponse
from app.services.embeddings import embed_query
from app.services.hybrid_search import hybrid_search

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Case Compass, a judicial research assistant.
Use ONLY the retrieved documents below to answer the user's question. If the answer
cannot be found in them, say "I could not find that in your documents."

{context}"""


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    """Create the Gemini client. Cached for the process lifetime."""
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set; it is required for answers.")

    log.info("Using Gemini LLM: %s", settings.gemini_model)
    return OpenAI(api_key=settings.gemini_api_key, base_url=settings.gemini_base_url)


def answer_question(
    db: Session,
    *,
    user_id: uuid.UUID,
    query: str,
    case_id: str | None = None,
    top_k: int = 5,
) -> SearchResponse:
    """Run the full RAG pipeline for one user query.

    Steps:
    1. Embed the query.
    2. Hybrid-search the user's own chunks (user-scoped by SQL filter).
    3. Build a prompt with the retrieved context.
    4. Generate an answer with the local HF LLM.
    """
    query_vec = embed_query(query)
    chunks = hybrid_search(
        db,
        user_id=user_id,
        query_text=query,
        query_embedding=query_vec,
        case_id=case_id,
        top_k=top_k,
    )

    if not chunks:
        return SearchResponse(
            query=query,
            answer="I could not find that in your documents.",
            hits=[],
        )

    context = "\n\n---\n\n".join(
        f"[{i + 1}] {c.content}" for i, c in enumerate(chunks)
    )
    response = _get_client().chat.completions.create(
        model=settings.gemini_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ],
    )
    answer_text = (response.choices[0].message.content or "").strip()

    hits = [
        SearchHit(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            document_title=c.document_title,
            content=c.content,
            score=c.score,
            case_id=c.case_id,
            chunk_index=c.chunk_index,
        )
        for c in chunks
    ]
    return SearchResponse(query=query, answer=answer_text, hits=hits)
