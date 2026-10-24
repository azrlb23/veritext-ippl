import uuid
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID, Vector


class CorpusDocument(Base):
    __tablename__ = "corpus_documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    uploaded_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    title = Column(String(500), nullable=False)
    category = Column(String(255), nullable=True, index=True)
    academic_year = Column(String(20), nullable=True)
    stored_filename = Column(String(500), nullable=False, unique=True)
    sha256_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="PENDING_INDEX", index=True)
    total_chunks = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING_INDEX', 'INDEXING', 'INDEXED', 'ERROR', 'DELETED')",
            name="chk_corpus_status",
        ),
        Index("idx_corpus_documents_uploaded_by", "uploaded_by"),
    )

    # Relationships
    uploader = relationship("User", back_populates="uploaded_corpus")
    chunks = relationship("DocumentChunk", back_populates="corpus_document", cascade="all, delete-orphan")
    fingerprints = relationship("LexicalFingerprint", back_populates="corpus_document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    corpus_doc_id = Column(GUID(), ForeignKey("corpus_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        UniqueConstraint("corpus_doc_id", "chunk_index", name="uq_document_chunks_corpus_chunk"),
    )

    # Relationship
    corpus_document = relationship("CorpusDocument", back_populates="chunks")


class LexicalFingerprint(Base):
    __tablename__ = "lexical_fingerprints"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    corpus_doc_id = Column(GUID(), ForeignKey("corpus_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    fingerprint_hash = Column(BigInteger, nullable=False, index=True)
    position_start = Column(Integer, nullable=True)
    position_end = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationship
    corpus_document = relationship("CorpusDocument", back_populates="fingerprints")
