import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer

from app.core.database import Base
from app.models.types import GUID


def utcnow():
    return datetime.now(timezone.utc)


class SystemConfig(Base):
    """
    Persistent system configuration & AI engine hyperparameters (Phase 6 / ROUND4-05).
    Stores aggregation weights (Tier 1-3), pgvector HNSW parameters, winnowing k-gram,
    similarity thresholds, and document retention period under UU PDP No. 27/2022.
    """
    __tablename__ = "system_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Aggregation weights Tier 1-3 (Lexical, Semantic, Stylometric)
    lexical_weight = Column(Float, nullable=False, default=0.50)
    semantic_weight = Column(Float, nullable=False, default=0.35)
    stylometric_weight = Column(Float, nullable=False, default=0.15)

    # Thresholds
    similarity_threshold = Column(Float, nullable=False, default=0.78)
    stylometric_burstiness_threshold = Column(Float, nullable=False, default=0.35)

    # Winnowing parameters
    winnowing_kgram = Column(Integer, nullable=False, default=5)
    winnowing_window = Column(Integer, nullable=False, default=4)

    # pgvector HNSW hyperparameters
    hnsw_ef_search = Column(Integer, nullable=False, default=64)
    hnsw_m = Column(Integer, nullable=False, default=16)

    # Document retention policy (UU PDP) in days
    retention_days = Column(Integer, nullable=False, default=30)

    # Operational mode
    sandbox_mode = Column(Boolean, nullable=False, default=False)

    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
