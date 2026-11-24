from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.invoice import Invoice
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.billing import MidtransWebhookPayload


def verify_midtrans_signature(payload: MidtransWebhookPayload) -> None:
    sig_keys = [k for k in (settings.MIDTRANS_SIGNATURE_KEY, settings.MIDTRANS_SERVER_KEY) if k]
    if not any(
        hmac.compare_digest(
            payload.signature_key,
            hashlib.sha512(
                f"{payload.order_id}{payload.status_code}{payload.gross_amount}{k}".encode("utf-8")
            ).hexdigest(),
        )
        for k in sig_keys
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Midtrans signature key")


def validate_invoice_amount(invoice: Invoice, gross_amount_str: str) -> None:
    try:
        payload_amount = float(gross_amount_str)
        invoice_amount = float(invoice.gross_amount) if invoice.gross_amount is not None else None
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gross amount format: {gross_amount_str}",
        )

    if invoice_amount is not None and abs(payload_amount - invoice_amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gross amount mismatch: expected {invoice.gross_amount}, got {gross_amount_str}",
        )


async def apply_paid_settlement(db: AsyncSession, invoice: Invoice, payload: MidtransWebhookPayload) -> None:
    invoice.status = "PAID"
    invoice.paid_at = datetime.now(timezone.utc)  # noqa: UP017
    invoice.payment_method = payload.payment_type or "bank_transfer"

    wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == invoice.user_id).with_for_update()
    wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
    if not wallet:
        wallet = TokenWallet(user_id=invoice.user_id, balance=0)
        db.add(wallet)
        await db.flush()

    wallet.balance += invoice.token_amount
    db.add(
        TokenTransaction(
            wallet_id=wallet.id,
            transaction_type="CREDIT_TOPUP",
            amount=invoice.token_amount,
            balance_after=wallet.balance,
            reference_id=invoice.id,
            note=f"Top-up {invoice.package_name}",
        )
    )

    user_stmt = select(User).where(User.id == invoice.user_id).with_for_update()
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if isinstance(user, User) and (user.role or "").upper() == "FREE":
        user.role = "PREMIUM"

    db.add(
        AuditLog(
            actor_id=invoice.user_id,
            action_type="BILLING_TOPUP",
            resource_type="INVOICE",
            resource_id=invoice.id,
            action_result="SUCCESS",
            meta_data={
                "order_id": invoice.order_id,
                "token_amount": invoice.token_amount,
                "gross_amount": int(invoice.gross_amount or 0),
            },
        )
    )
