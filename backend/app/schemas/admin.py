from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, field_validator


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    institution: Optional[str] = None
    role: str
    is_active: bool = True
    failed_login_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool
    reason: Optional[str] = None


class AdminUserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(default="VeriText#2026", min_length=6)
    institution: Optional[str] = None
    role: str = Field(default="TRIAL")
    initial_tokens: int = Field(default=10, ge=0, le=1_000_000)


class AdminUserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    institution: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, description="New password set by administrator")


class TokenAdjustmentRequest(BaseModel):
    amount: int = Field(..., ge=-1_000_000, le=1_000_000, description="Positive to credit, negative to debit")
    note: str = Field(..., min_length=3)


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


class SystemConfigRequest(BaseModel):
    # Aggregation weights Tier 1-3
    lexical_weight: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("lexical_weight", "similarity_lexical_weight"),
    )
    semantic_weight: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("semantic_weight", "similarity_semantic_weight"),
    )
    stylometric_weight: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("stylometric_weight", "similarity_stylo_weight"),
    )

    # Thresholds
    similarity_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("similarity_threshold", "hnsw_similarity_threshold"),
    )
    stylometric_burstiness_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Winnowing parameters
    winnowing_kgram: Optional[int] = Field(default=None, ge=1, le=100)
    winnowing_window: Optional[int] = Field(default=None, ge=1, le=100)

    # HNSW parameters
    hnsw_ef_search: Optional[int] = Field(default=None, ge=1, le=1024)
    hnsw_m: Optional[int] = Field(default=None, ge=2, le=128)

    # Data retention period in days (UU PDP)
    retention_days: Optional[int] = Field(default=None, ge=1, le=3650)

    # Operational sandbox mode
    sandbox_mode: Optional[bool] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class SystemConfigResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    lexical_weight: float = 0.50
    semantic_weight: float = 0.35
    stylometric_weight: float = 0.15
    similarity_threshold: float = 0.78
    hnsw_similarity_threshold: float = 0.78
    stylometric_burstiness_threshold: float = 0.35
    winnowing_kgram: int = 5
    winnowing_window: int = 4
    hnsw_ef_search: int = 64
    hnsw_m: int = 16
    retention_days: int = 30
    sandbox_mode: bool = False
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

