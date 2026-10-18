import uuid
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID


class Document(Base):
    __tablename__ = "documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False, unique=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    word_count = Column(Integer, nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    status = Column(String(50), nullable=False, default="UPLOADED", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft-delete for UU PDP audit trail

    __table_args__ = (
        CheckConstraint(
            "status IN ('UPLOADED', 'PROCESSING', 'READY', 'ERROR', 'DELETED')",
            name="chk_document_status",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="documents")
    audit_tasks = relationship("AuditTask", back_populates="document", cascade="all, delete-orphan")
