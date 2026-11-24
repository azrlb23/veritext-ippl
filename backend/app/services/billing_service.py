from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.billing import MidtransWebhookPayload
from app.services.billing_packages import PACKAGES, resolve_package  # noqa: F401
from app.services.billing_webhook_helper import (
    apply_paid_settlement,
    validate_invoice_amount,
    verify_midtrans_signature,
)
from app.services.midtrans_snap import create_snap_token


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
    async def get_recent_transactions(
        db: AsyncSession, wallet_id: uuid.UUID, limit: int = 10
    ) -> list[TokenTransaction]:
        stmt = (
            select(TokenTransaction)
            .where(TokenTransaction.wallet_id == wallet_id)
            .order_by(TokenTransaction.created_at.desc())
            .limit(limit)
        )
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def create_topup_invoice(
        db: AsyncSession,
        user_id: uuid.UUID,
        package_id: str,
        token_amount: int | None = None,
        customer: dict | None = None,
    ) -> Invoice:
        pkg = resolve_package(package_id, token_amount)
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")  # noqa: UP017
        order_id = f"VT-{date_str}-{uuid.uuid4().hex[:12].upper()}"
        snap_token = (
            await create_snap_token(order_id, pkg["price"], pkg["name"], pkg["tokens"], customer or {})
            or f"SNAP-{uuid.uuid4().hex}"
        )

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
        if payload.order_id.startswith("payment_notif_test_"):
            return True

        verify_midtrans_signature(payload)

        stmt = select(Invoice).where(Invoice.order_id == payload.order_id).with_for_update()
        invoice = (await db.execute(stmt)).scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice order not found")

        validate_invoice_amount(invoice, payload.gross_amount)

        if invoice.status == "PAID":
            return True

        if payload.transaction_status in ("capture", "settlement"):
            fraud_stat = getattr(payload, "fraud_status", None)
            if fraud_stat and fraud_stat != "accept":
                invoice.status = "CHALLENGE" if fraud_stat == "challenge" else "FAILED"
            else:
                await apply_paid_settlement(db, invoice, payload)
        elif payload.transaction_status in ("cancel", "expire"):
            invoice.status = "EXPIRED" if payload.transaction_status == "expire" else "CANCEL"
        elif payload.transaction_status in ("deny", "failed"):
            invoice.status = "FAILED"

        await db.commit()
        return True
