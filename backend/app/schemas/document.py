from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    file_size_bytes: int
    mime_type: str
    word_count: Optional[int] = None
    sha256_hash: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    celery_task_id: Optional[str] = None
    original_filename: str
    message: str
