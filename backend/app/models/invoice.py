import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID


def default_expires_at():
    return datetime.now(timezone.utc) + timedelta(hours=24)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(String(100), nullable=False, unique=True, index=True)
    snap_token = Column(Text, nullable=True)
    package_name = Column(String(100), nullable=False)
    token_amount = Column(Integer, nullable=False)
    gross_amount = Column(BigInteger, nullable=False)  # in IDR (cents or full rupiah)
    payment_method = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    midtrans_transaction_id = Column(String(255), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, default=default_expires_at)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCEL')",
            name="chk_invoice_status",
        ),
    )

    # Relationship
    user = relationship("User", back_populates="invoices")
