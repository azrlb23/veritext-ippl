import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, SmallInteger, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    institution = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="TRIAL", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    failed_login_count = Column(SmallInteger, nullable=False, default=0)
    lockout_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    token_wallet = relationship("TokenWallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    audit_tasks = relationship("AuditTask", back_populates="user")
    uploaded_corpus = relationship("CorpusDocument", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="actor")

    @property
    def token_balance(self) -> int:
        try:
            return self.token_wallet.balance if self.token_wallet else 0
        except Exception:
            return 0
