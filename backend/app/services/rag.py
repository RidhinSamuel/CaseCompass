"""RAG orchestrator — glues embeddings, hybrid search, and an LLM together.

The LLM is a small open-source HuggingFace model (default: flan-t5-base)
so the whole pipeline runs without paid API calls.
"""
import logging
import uuid
from functools import lru_cache

from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.document import SearchHit, SearchResponse
from app.services.embeddings import embed_query
from app.services.hybrid_search import hybrid_search

log = logging.getLogger(__name__)

_ANSWER_PROMPT = """You are Case Compass, a judicial research assistant.
Use ONLY the context below to answer the user's question. If the answer
cannot be found in the context, say "I could not find that in your documents."

Context:
{context}

Question: {question}
Answer:"""


@lru_cache(maxsize=1)
def _get_llm():
    """Lazy-load a small HF text2text model. Cached for the process lifetime."""
    from transformers import pipeline  # local import: heavy

    log.info("Loading LLM: %s", settings.hf_llm_model)
    return pipeline(
        "text2text-generation",
        model=settings.hf_llm_model,
        max_new_tokens=256,
    )


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
    prompt = _ANSWER_PROMPT.format(context=context, question=query)

    llm = _get_llm()
    result = llm(prompt)
    answer_text = result[0]["generated_text"].strip() if result else ""

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
