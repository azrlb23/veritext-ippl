import uuid
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID

JsonType = JSON().with_variant(JSONB, "postgresql")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    actor_id = Column(GUID(), ForeignKey("users.id"), nullable=True, index=True)
    actor_ip = Column(String(45), nullable=True)
    actor_user_agent = Column(Text, nullable=True)
    action_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(GUID(), nullable=True)
    action_result = Column(String(50), nullable=False, default="SUCCESS")
    meta_data = Column("metadata", JsonType, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint(
            "action_result IN ('SUCCESS', 'FAILURE', 'BLOCKED')",
            name="chk_audit_log_action_result",
        ),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
    )

    # Relationship
    actor = relationship("User", back_populates="audit_logs")
