import uuid
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import GUID


class TokenWallet(Base):
    __tablename__ = "token_wallets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    balance = Column(Integer, nullable=False, default=0)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_wallet_balance_positive"),
    )

    # Relationships
    user = relationship("User", back_populates="token_wallet")
    transactions = relationship("TokenTransaction", back_populates="wallet", cascade="all, delete-orphan")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(GUID(), ForeignKey("token_wallets.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    reference_id = Column(GUID(), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('DEBIT_AUDIT', 'CREDIT_TOPUP', 'CREDIT_REFUND', 'CREDIT_ADMIN', 'DEBIT_ADMIN')",
            name="chk_transaction_type",
        ),
    )

    # Relationship
    wallet = relationship("TokenWallet", back_populates="transactions")
