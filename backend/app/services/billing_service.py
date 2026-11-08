from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.invoice import Invoice
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.billing import MidtransWebhookPayload
from app.services.midtrans_snap import create_snap_token
from app.services.billing_packages import PACKAGES, resolve_package  # noqa: F401

class BillingService:
    @staticmethod
    async def get_wallet(db: AsyncSession, user_id: uuid.UUID) -> TokenWallet:
        stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
        wallet = (await db.execute(stmt)).scalar_one_or_none()
        if not wallet:
            wallet = TokenWallet(user_id=user_id, balance=0)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        return wallet

    @staticmethod
    async def create_topup_invoice(
        db: AsyncSession, user_id: uuid.UUID, package_id: str, token_amount: int | None = None, customer: dict | None = None
    ) -> Invoice:
        pkg = resolve_package(package_id, token_amount)
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")  # noqa: UP017
        order_id = f"VT-{date_str}-{uuid.uuid4().hex[:12].upper()}"
        snap_token = await create_snap_token(order_id, pkg["price"], pkg["name"], pkg["tokens"], customer or {}) or f"SNAP-{uuid.uuid4().hex}"

        invoice = Invoice(
            user_id=user_id,
            order_id=order_id,
            snap_token=snap_token,
            package_name=pkg["name"],
            token_amount=pkg["tokens"],
            gross_amount=pkg["price"],
            status="PENDING",
        )
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def process_midtrans_webhook(db: AsyncSession, payload: MidtransWebhookPayload) -> bool:
        expected_sig_raw = f"{payload.order_id}{payload.status_code}{payload.gross_amount}{settings.MIDTRANS_SERVER_KEY}"
        expected_signature = hashlib.sha512(expected_sig_raw.encode("utf-8")).hexdigest()

        if not hmac.compare_digest(payload.signature_key, expected_signature):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Midtrans signature key")

        stmt = select(Invoice).where(Invoice.order_id == payload.order_id).with_for_update()
        invoice = (await db.execute(stmt)).scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice order not found")

        try:
            payload_amount = float(payload.gross_amount)
            invoice_amount = float(invoice.gross_amount) if invoice.gross_amount is not None else None
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid gross amount format: {payload.gross_amount}")

        if invoice_amount is not None and abs(payload_amount - invoice_amount) > 0.01:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gross amount mismatch: expected {invoice.gross_amount}, got {payload.gross_amount}")

        if invoice.status == "PAID":
            return True

        if payload.transaction_status in ("capture", "settlement"):
            fraud_stat = getattr(payload, "fraud_status", None)
            if fraud_stat and fraud_stat != "accept":
                invoice.status = "CHALLENGE" if fraud_stat == "challenge" else "FAILED"
            else:
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
                tx = TokenTransaction(
                    wallet_id=wallet.id,
                    transaction_type="CREDIT_TOPUP",
                    amount=invoice.token_amount,
                    balance_after=wallet.balance,
                    reference_id=invoice.id,
                    note=f"Top-up {invoice.package_name}",
                )
                db.add(tx)
        elif payload.transaction_status in ("cancel", "expire"):
            invoice.status = "EXPIRED" if payload.transaction_status == "expire" else "CANCEL"
        elif payload.transaction_status in ("deny", "failed"):
            invoice.status = "FAILED"

        await db.commit()
        return True
