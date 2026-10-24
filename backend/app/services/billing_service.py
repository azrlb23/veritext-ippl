from datetime import datetime, timezone
import hashlib
import hmac
from typing import Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.invoice import Invoice
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.billing import MidtransWebhookPayload


PACKAGES = {
    "pkg_10token": {"name": "Paket Mahasiswa (10 Token)", "tokens": 10, "price": 25000},
    "pkg_50token": {"name": "Paket Peneliti (50 Token)", "tokens": 50, "price": 100000},
    "pkg_200token": {"name": "Paket Institusi (200 Token)", "tokens": 200, "price": 350000},
}


class BillingService:
    @staticmethod
    async def get_wallet(db: AsyncSession, user_id: uuid.UUID) -> TokenWallet:
        stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = TokenWallet(user_id=user_id, balance=0)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        return wallet

    @staticmethod
    async def create_topup_invoice(
        db: AsyncSession, user_id: uuid.UUID, package_id: str
    ) -> Invoice:
        if package_id not in PACKAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid package_id. Available: {', '.join(PACKAGES.keys())}",
            )

        pkg = PACKAGES[package_id]
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        order_id = f"VT-{date_str}-{uuid.uuid4().hex[:12].upper()}"

        # Demo / Sandbox snap token
        snap_token = f"SNAP-{uuid.uuid4().hex}"

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
    async def process_midtrans_webhook(
        db: AsyncSession, payload: MidtransWebhookPayload
    ) -> bool:
        # Validate signature key according to Midtrans specs:
        # SHA512(order_id + status_code + gross_amount + ServerKey)
        expected_sig_raw = (
            f"{payload.order_id}{payload.status_code}{payload.gross_amount}{settings.MIDTRANS_SERVER_KEY}"
        )
        expected_signature = hashlib.sha512(expected_sig_raw.encode("utf-8")).hexdigest()

        # Constant-time comparison using hmac.compare_digest
        if not hmac.compare_digest(payload.signature_key, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Midtrans signature key",
            )

        # Row-level locking on Invoice to prevent race conditions & double-crediting
        stmt = select(Invoice).where(Invoice.order_id == payload.order_id).with_for_update()
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice order not found",
            )

        # Strict validation: gross_amount in payload must match invoice record
        try:
            payload_amount = float(payload.gross_amount)
            invoice_amount = float(invoice.gross_amount) if invoice.gross_amount is not None else None
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid gross amount format: {payload.gross_amount}",
            )

        if invoice_amount is not None and abs(payload_amount - invoice_amount) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Gross amount mismatch: expected {invoice.gross_amount}, got {payload.gross_amount}",
            )

        if invoice.status == "PAID":
            return True

        if payload.transaction_status in ("capture", "settlement"):
            # If fraud_status is present, verify that it is 'accept'
            fraud_stat = getattr(payload, "fraud_status", None)
            if fraud_stat and fraud_stat != "accept":
                invoice.status = "CHALLENGE" if fraud_stat == "challenge" else "FAILED"
            else:
                invoice.status = "PAID"
                invoice.paid_at = datetime.now(timezone.utc)
                invoice.payment_method = payload.payment_type or "bank_transfer"

                # Credit wallet with row-level locking
                wallet_stmt = (
                    select(TokenWallet)
                    .where(TokenWallet.user_id == invoice.user_id)
                    .with_for_update()
                )
                wallet_res = await db.execute(wallet_stmt)
                wallet = wallet_res.scalar_one_or_none()
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
