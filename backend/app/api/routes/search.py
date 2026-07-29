"""Search endpoint: hybrid retrieval + LLM answer, scoped to the current user."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import SearchRequest, SearchResponse
from app.services.rag import answer_question

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    """Run RAG for the current user's documents only."""
    return answer_question(
        db,
        user_id=current_user.id,
        query=payload.query,
        case_id=payload.case_id,
        top_k=payload.top_k,
    )
