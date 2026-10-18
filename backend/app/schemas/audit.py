from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
import uuid
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class AuditStartRequest(BaseModel):
    document_id: uuid.UUID
    audit_depth: str = Field("FULL", pattern="^(TIER1_ONLY|FULL)$")


class AuditTaskStatusResponse(BaseModel):
    id: Optional[uuid.UUID] = Field(None, validation_alias=AliasChoices("id", "task_id"))
    task_id: uuid.UUID = Field(validation_alias=AliasChoices("task_id", "id"))
    document_id: uuid.UUID
    celery_task_id: Optional[str] = None
    audit_depth: str
    status: str
    progress_pct: int
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    document_title: Optional[str] = None
    score_composite: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HeatmapAnnotation(BaseModel):
    start: int
    end: int
    tier: str  # T1, T2, T3
    color: str  # RED, ORANGE, YELLOW
    source_title: Optional[str] = None
    source_chunk_id: Optional[str] = None
    similarity: float
    text_snippet: Optional[str] = None


class MatchedSource(BaseModel):
    corpus_doc_id: str
    title: str
    category: Optional[str] = None
    contribution_pct: float


class AuditReportResponse(BaseModel):
    id: uuid.UUID
    audit_task_id: uuid.UUID
    verification_uuid: uuid.UUID
    score_lexical: Optional[Decimal] = None
    score_semantic: Optional[Decimal] = None
    score_stylometric: Optional[Decimal] = None
    score_composite: Optional[Decimal] = None
    heatmap_annotations: List[Any] = Field(default_factory=list)
    matched_sources: List[Any] = Field(default_factory=list)
    pdf_path: Optional[str] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditVerificationResponse(BaseModel):
    is_valid: bool
    verification_uuid: str
    document_title: Optional[str] = None
    user_name: Optional[str] = None
    institution: Optional[str] = None
    audit_date: Optional[datetime] = None
    score_composite: Optional[float] = None
    tier_scores: Optional[dict] = None
    message: str
