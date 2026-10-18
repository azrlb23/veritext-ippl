from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class TopupRequest(BaseModel):
    package_id: str = Field(..., description="Package identifier, e.g. pkg_10token, pkg_50token")


class TopupResponse(BaseModel):
    order_id: str
    snap_token: Optional[str] = None
    gross_amount: int
    package_name: str
    token_amount: int


class TokenTransactionResponse(BaseModel):
    id: uuid.UUID
    transaction_type: str
    amount: int
    balance_after: int
    reference_id: Optional[uuid.UUID] = None
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenWalletResponse(BaseModel):
    id: uuid.UUID
    balance: int
    updated_at: datetime
    recent_transactions: List[TokenTransactionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    order_id: str
    package_name: str
    token_amount: int
    gross_amount: int
    payment_method: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MidtransWebhookPayload(BaseModel):
    order_id: str
    status_code: str
    gross_amount: str
    signature_key: str
    transaction_status: str
    payment_type: Optional[str] = None
    transaction_id: Optional[str] = None

    model_config = ConfigDict(extra="allow")
