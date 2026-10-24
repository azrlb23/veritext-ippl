import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        Index("idx_password_resets_user_id", "user_id"),
    )

    # Relationship
    user = relationship("User", back_populates="password_resets")

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @is_used.setter
    def is_used(self, value: bool) -> None:
        from datetime import datetime, timezone
        if value:
            self.used_at = datetime.now(timezone.utc)
        else:
            self.used_at = None
