from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class SystemHealthMetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    database_status: str
    redis_status: str
    celery_active_tasks: int
    db_latency_ms: float
    timestamp: datetime
    total_audits: int = 0
    total_corpus_docs: int = 0
    total_vector_chunks: int = 0
    celery_workers: int = 1
    queue_depth: int = 0
    redis_mem_mb: float = 12.5
    pgvector_latency_ms: float = 4.2


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    actor_ip: Optional[str] = None
    action_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[uuid.UUID] = None
    action_result: str
    meta_data: Dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("meta_data", "metadata"),
        serialization_alias="metadata",
    )
    created_at: datetime

    @field_validator("meta_data", mode="before")
    @classmethod
    def sanitize_metadata(cls, v: Any) -> Dict[str, Any]:
        if isinstance(v, dict):
            return v
        return {}

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserItem(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    balance: int
    ai_trial_remaining: int
    audit_count: int
    is_locked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrendPoint(BaseModel):
    date: str
    audits: int
    revenue: int

    model_config = ConfigDict(from_attributes=True)


class OverviewExtras(BaseModel):
    new_users_7d: int
    audits_today: int
    tokens_spent_30d: int
    role_distribution: Dict[str, int]
    trends: list[TrendPoint]

    model_config = ConfigDict(from_attributes=True)


class InvoiceSummary(BaseModel):
    total_revenue: int
    paid: int
    pending: int
    failed: int
    top_package: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SystemExtras(BaseModel):
    failed_audits_24h: int
    queued_audits: int
    processing_audits: int

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "AdminUserItem",
    "AuditLogResponse",
    "InvoiceSummary",
    "OverviewExtras",
    "SystemExtras",
    "SystemHealthMetricsResponse",
    "TrendPoint",
]
