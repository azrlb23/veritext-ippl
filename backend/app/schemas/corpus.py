from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class CorpusDocResponse(BaseModel):
    id: uuid.UUID
    uploaded_by: uuid.UUID
    title: str
    category: Optional[str] = None
    academic_year: Optional[str] = None
    stored_filename: str
    sha256_hash: str
    status: str
    total_chunks: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CorpusDocUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=500)
    category: Optional[str] = Field(None, max_length=255)
    academic_year: Optional[str] = Field(None, max_length=20)


class CorpusIngestResponse(BaseModel):
    queued_count: int
    message: str
