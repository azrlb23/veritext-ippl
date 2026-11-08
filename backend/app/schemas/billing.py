from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class TopupRequest(BaseModel):
    package_id: str = Field(..., description="pkg_starter, pkg_skripsi_pro, pkg_riset_intensif, atau pkg_tokens (satuan)")
    token_amount: Optional[int] = Field(None, ge=1, le=500, description="Wajib untuk pkg_tokens: jumlah token (min 5)")


class TopupResponse(BaseModel):
    order_id: str
    snap_token: Optional[str] = None
    gross_amount: int
    package_name: str
    token_amount: int
    payment_ready: bool = False
    client_key: Optional[str] = None


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
