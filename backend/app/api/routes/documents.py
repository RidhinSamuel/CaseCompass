"""Document endpoints: upload (as raw text) and list your own docs."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.queue.rabbitmq import rabbitmq
from app.schemas.document import DocumentCreate, DocumentRead

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    """Store the raw document and publish an ingestion job.

    The heavy work (chunking + embedding) is done by workers so the API
    returns quickly even under bursty upload traffic.
    """
    doc = Document(
        user_id=current_user.id,
        case_id=payload.case_id,
        title=payload.title,
        raw_text=payload.raw_text,
        status="pending",
        doc_metadata=payload.metadata,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    await rabbitmq.publish({"document_id": str(doc.id)})
    return doc


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    """List documents owned by the current user."""
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    doc = db.get(Document, document_id)
    if doc is None or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
