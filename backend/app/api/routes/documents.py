"""Document endpoints: upload (raw text or PDF) and list your own docs."""
import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.queue.rabbitmq import rabbitmq
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.pdf_extract import PdfExtractionError, extract_pdf_text

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Matches `client_max_body_size 10m` in frontend/nginx.conf.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


async def _save_and_queue(
    db: Session,
    user: User,
    *,
    title: str,
    case_id: str | None,
    raw_text: str,
    metadata: dict,
    source_filename: str | None = None,
    mime_type: str | None = None,
) -> Document:
    """Persist a pending document and publish its ingestion job."""
    doc = Document(
        user_id=user.id,
        case_id=case_id,
        title=title,
        source_filename=source_filename,
        mime_type=mime_type,
        raw_text=raw_text,
        status="pending",
        doc_metadata=metadata,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    await _queue(doc.id)
    return doc


async def _queue(document_id: uuid.UUID) -> None:
    """Publish an ingestion job; a broker outage leaves the document pending."""
    try:
        await rabbitmq.publish({"document_id": str(document_id)})
    except Exception:  # noqa: BLE001
        log.exception(
            "Could not queue ingestion job for document %s; document is saved and remains pending",
            document_id,
        )


def _get_owned(db: Session, user: User, document_id: uuid.UUID) -> Document:
    """Return the user's document, or 404 (also for other users' documents)."""
    doc = db.get(Document, document_id)
    if doc is None or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


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
    return await _save_and_queue(
        db,
        current_user,
        title=payload.title,
        case_id=payload.case_id,
        raw_text=payload.raw_text,
        metadata=payload.metadata,
    )


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(..., min_length=1, max_length=512),
    case_id: str | None = Form(None, max_length=128),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    """Accept a PDF, extract its text, then queue ingestion like a text upload."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only .pdf files are supported"
        )

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large (max 10 MB)"
        )
    if not data.startswith(b"%PDF-"):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File content is not a valid PDF"
        )

    try:
        text, pages = await asyncio.to_thread(extract_pdf_text, data)
    except PdfExtractionError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    return await _save_and_queue(
        db,
        current_user,
        title=title,
        case_id=case_id or None,
        raw_text=text,
        metadata={"page_count": pages},
        source_filename=filename[:512],
        mime_type="application/pdf",
    )


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    """List documents owned by the current user."""
    return list(
        db.execute(
            select(Document)
            .where(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
        )
        .scalars()
        .all()
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    return _get_owned(db, current_user, document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a document; its chunks are removed by the ON DELETE CASCADE."""
    doc = _get_owned(db, current_user, document_id)
    db.delete(doc)
    db.commit()


@router.post("/{document_id}/retry", response_model=DocumentRead)
async def retry_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    """Re-queue a failed document using its stored text (no re-upload needed)."""
    doc = _get_owned(db, current_user, document_id)
    if doc.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only failed documents can be retried (status is '{doc.status}')",
        )
    doc.status = "pending"
    db.commit()
    db.refresh(doc)
    await _queue(doc.id)
    return doc
