from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.types import GUID

JsonType = JSON().with_variant(JSONB, "postgresql")


class AuditTask(Base):
    __tablename__ = "audit_tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    audit_depth = Column(String(50), nullable=False, default="FULL")
    status = Column(String(50), nullable=False, default="QUEUED", index=True)
    progress_pct = Column(SmallInteger, nullable=False, default=0)
    current_stage = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint("audit_depth IN ('TIER1_ONLY', 'FULL')", name="chk_audit_depth"),
        CheckConstraint("status IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'SUCCESS', 'FAILED', 'CANCELLED', 'REVOKED')", name="chk_audit_status"),
        CheckConstraint("progress_pct BETWEEN 0 AND 100", name="chk_progress_pct"),
    )

    document = relationship("Document", back_populates="audit_tasks")
    user = relationship("User", back_populates="audit_tasks")
    sentences = relationship("AuditSentence", back_populates="audit_task", cascade="all, delete-orphan")
    report = relationship("AuditReport", back_populates="audit_task", uselist=False, cascade="all, delete-orphan")

    @property
    def task_id(self) -> uuid.UUID:
        return self.id

    @property
    def document_title(self) -> str | None:
        return getattr(self.document, "original_filename", None) if self.document else None

    @property
    def score_composite(self) -> float | None:
        return float(self.report.score_composite) if (self.report and self.report.score_composite is not None) else None


class AuditSentence(Base):
    __tablename__ = "audit_sentences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    audit_task_id = Column(GUID(), ForeignKey("audit_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    sentence_index = Column(Integer, nullable=False)
    sentence_text = Column(Text, nullable=False)
    current_text = Column(Text, nullable=True)
    match_type = Column(String(20), nullable=False, default="NONE")
    similarity_score = Column(Numeric(5, 2), nullable=False, default=0)
    matched_source_id = Column(GUID(), nullable=True)
    is_modified = Column(Boolean, nullable=False, default=False)
    start_char = Column(Integer, nullable=False, default=0)
    end_char = Column(Integer, nullable=False, default=0)
    word_count = Column(SmallInteger, nullable=False, default=0)
    is_citation = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("audit_task_id", "sentence_index", name="uq_audit_task_sentence_index"),
        CheckConstraint("match_type IN ('NONE', 'RED', 'ORANGE', 'YELLOW', 'RESOLVED_GREEN')", name="chk_sentence_match_type"),
    )

    audit_task = relationship("AuditTask", back_populates="sentences")

    @property
    def sentence_order(self) -> int: return self.sentence_index

    @property
    def original_text(self) -> str: return self.sentence_text


class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    audit_task_id = Column(GUID(), ForeignKey("audit_tasks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    verification_uuid = Column(GUID(), nullable=False, unique=True, default=uuid.uuid4, index=True)
    score_lexical = Column(Numeric(5, 2), nullable=True)
    score_semantic = Column(Numeric(5, 2), nullable=True)
    score_stylometric = Column(Numeric(5, 2), nullable=True)
    score_composite = Column(Numeric(5, 2), nullable=True)
    heatmap_annotations = Column(JsonType, nullable=False, default=list)
    matched_sources = Column(JsonType, nullable=False, default=list)
    pdf_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    audit_task = relationship("AuditTask", back_populates="report")

    @property
    def certificate_uuid(self) -> uuid.UUID:
        return self.verification_uuid

    @property
    def document_title(self) -> str | None:
        return self.audit_task.document.original_filename if (self.audit_task and self.audit_task.document) else None

    @property
    def user_name(self) -> str | None:
        return self.audit_task.user.full_name if (self.audit_task and self.audit_task.user) else None

    @property
    def document_text(self) -> str | None:
        if getattr(self, "_document_text", None) is not None:
            return self._document_text
        if self.audit_task and self.audit_task.sentences:
            ordered = sorted(self.audit_task.sentences, key=lambda s: getattr(s, "sentence_index", 0))
            return " ".join((s.current_text or s.sentence_text or "") for s in ordered).strip() or None
        return None

    @document_text.setter
    def document_text(self, val: str | None):
        self._document_text = val
