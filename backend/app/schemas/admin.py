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


__all__ = [
    "AuditLogResponse",
    "SystemHealthMetricsResponse",
]
