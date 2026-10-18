from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    institution: Optional[str] = None
    role: str
    is_active: bool
    failed_login_count: int
    created_at: datetime

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
    initial_tokens: int = Field(default=10, ge=0)


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
    amount: int = Field(..., description="Positive to credit, negative to debit")
    note: str = Field(..., min_length=3)


class SystemHealthMetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    database_status: str
    redis_status: str
    celery_active_tasks: int
    db_latency_ms: float
    timestamp: datetime


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    actor_ip: Optional[str] = None
    action_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[uuid.UUID] = None
    action_result: str
    meta_data: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("metadata", "meta_data"), serialization_alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
