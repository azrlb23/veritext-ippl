import uuid
from typing import Optional
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
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID

# Use JSONB on PostgreSQL for efficient indexing, standard JSON elsewhere
JsonType = JSON().with_variant(JSONB, "postgresql")


class AuditTask(Base):
    __tablename__ = "audit_tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
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
        CheckConstraint(
            "status IN ('QUEUED', 'PROCESSING', 'SUCCESS', 'FAILED', 'CANCELLED', 'REVOKED')",
            name="chk_audit_status",
        ),
        CheckConstraint("progress_pct BETWEEN 0 AND 100", name="chk_progress_pct"),
    )

    # Relationships
    document = relationship("Document", back_populates="audit_tasks")
    user = relationship("User", back_populates="audit_tasks")
    sentences = relationship("AuditSentence", back_populates="audit_task", cascade="all, delete-orphan")
    report = relationship("AuditReport", back_populates="audit_task", uselist=False, cascade="all, delete-orphan")

    @property
    def task_id(self) -> uuid.UUID:
        return self.id

    @property
    def document_title(self) -> Optional[str]:
        try:
            return self.document.original_filename if self.document else None
        except Exception:
            return None

    @property
    def score_composite(self) -> Optional[float]:
        try:
            if self.report and self.report.score_composite is not None:
                return float(self.report.score_composite)
            return None
        except Exception:
            return None


class AuditSentence(Base):
    __tablename__ = "audit_sentences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    audit_task_id = Column(GUID(), ForeignKey("audit_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    sentence_index = Column(Integer, nullable=False)
    sentence_text = Column(Text, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    word_count = Column(SmallInteger, nullable=False)
    is_citation = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("audit_task_id", "sentence_index", name="uq_audit_task_sentence_index"),
    )

    # Relationship
    audit_task = relationship("AuditTask", back_populates="sentences")


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

    # Relationship
    audit_task = relationship("AuditTask", back_populates="report")

    @property
    def document_title(self) -> Optional[str]:
        try:
            return self.audit_task.document.original_filename if self.audit_task and self.audit_task.document else None
        except Exception:
            return None

    @property
    def user_name(self) -> Optional[str]:
        try:
            return self.audit_task.user.full_name if self.audit_task and self.audit_task.user else None
        except Exception:
            return None

    @property
    def institution(self) -> Optional[str]:
        try:
            return self.audit_task.user.institution if self.audit_task and self.audit_task.user else None
        except Exception:
            return None

    @property
    def document_text(self) -> Optional[str]:
        if hasattr(self, "_document_text") and self._document_text is not None:
            return self._document_text
        try:
            if self.audit_task and self.audit_task.document and self.audit_task.document.stored_filename:
                import os
                from app.core.config import settings
                from app.engine.preprocessor import TextPreprocessor
                fpath = os.path.join(settings.UPLOAD_DIR, self.audit_task.document.stored_filename)
                if os.path.exists(fpath):
                    raw_text = TextPreprocessor.extract_text_from_file(fpath, getattr(self.audit_task.document, "mime_type", None))
                    if raw_text and raw_text.strip():
                        return raw_text
        except Exception:
            pass
        try:
            if self.audit_task and self.audit_task.sentences:
                sorted_sentences = sorted(self.audit_task.sentences, key=lambda s: getattr(s, "sentence_index", 0))
                if sorted_sentences:
                    buf = []
                    curr_pos = 0
                    for s in sorted_sentences:
                        s_text = getattr(s, "sentence_text", "") or ""
                        s_start = getattr(s, "start_char", curr_pos)
                        if s_start is None:
                            s_start = curr_pos
                        if s_start > curr_pos:
                            buf.append(" " * (s_start - curr_pos))
                            curr_pos = s_start
                        buf.append(s_text)
                        curr_pos += len(s_text)
                    reconstructed = "".join(buf)
                    if reconstructed.strip():
                        return reconstructed
        except Exception:
            pass
        return None

    @document_text.setter
    def document_text(self, val: Optional[str]):
        self._document_text = val


