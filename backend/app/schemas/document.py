"""Pydantic schemas for documents and search results."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    case_id: str | None = Field(default=None, max_length=128)
    raw_text: str = Field(min_length=1)
    metadata: dict = Field(default_factory=dict)


class DocumentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    case_id: str | None
    title: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1024)
    case_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    score: float
    case_id: str | None
    chunk_index: int


class SearchResponse(BaseModel):
    query: str
    answer: str
    hits: list[SearchHit]
