import uuid
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.types import GUID

JsonType = JSON().with_variant(JSONB, "postgresql")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="Konsultasi Naskah")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    document_links = relationship("ChatSessionDocument", cascade="all, delete-orphan")


class ChatSessionDocument(Base):
    """Relasi banyak-ke-banyak: naskah yang dipakai sebagai konteks sebuah sesi asisten."""

    __tablename__ = "chat_session_documents"

    session_id = Column(GUID(), ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="USER")
    content = Column(Text, nullable=False)
    mode = Column(String(30), nullable=True, default="CONSULTATION")
    suggested_options = Column(JsonType, nullable=True)
    applied_to_document = Column(Boolean, nullable=False, default=False)
    target_sentence_id = Column(GUID(), ForeignKey("audit_sentences.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('USER', 'ASSISTANT', 'SYSTEM')", name="chk_chat_message_role"),
        CheckConstraint(
            "mode IS NULL OR mode IN ('CONSULTATION', 'SENTENCE', 'PARAGRAPH', 'FULL_PAGE')",
            name="chk_chat_message_mode",
        ),
    )

    session = relationship("ChatSession", back_populates="messages")
