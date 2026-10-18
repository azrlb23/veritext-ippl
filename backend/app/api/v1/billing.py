from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.billing import (
    InvoiceResponse,
    MidtransWebhookPayload,
    TokenTransactionResponse,
    TokenWalletResponse,
    TopupRequest,
    TopupResponse,
)
from app.schemas.common import APIResponse, PaginatedData
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/wallet", response_model=APIResponse[TokenWalletResponse])
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = await BillingService.get_wallet(db, current_user.id)
    return APIResponse(
        message="Token wallet retrieved",
        data=TokenWalletResponse(
            id=wallet.id,
            balance=wallet.balance,
            updated_at=wallet.updated_at,
            recent_transactions=[],
        ),
    )


@router.post("/topup", response_model=APIResponse[TopupResponse], status_code=status.HTTP_201_CREATED)
async def topup_tokens(
    req: TopupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invoice = await BillingService.create_topup_invoice(db, current_user.id, req.package_id)
    return APIResponse(
        message="Topup order created. Proceed to payment gateway.",
        data=TopupResponse(
            order_id=invoice.order_id,
            snap_token=invoice.snap_token,
            gross_amount=invoice.gross_amount,
            package_name=invoice.package_name,
            token_amount=invoice.token_amount,
        ),
    )


@router.post("/webhook")
async def midtrans_webhook(
    payload: MidtransWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
    await BillingService.process_midtrans_webhook(db, payload)
    return {"status": "OK", "message": "Webhook processed successfully"}


@router.get("/invoices", response_model=APIResponse[List[InvoiceResponse]])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Invoice)
        .where(Invoice.user_id == current_user.id)
        .order_by(Invoice.created_at.desc())
    )
    items = (await db.execute(stmt)).scalars().all()
    return APIResponse(
        message="Invoices retrieved",
        data=[InvoiceResponse.model_validate(x) for x in items],
    )


@router.get("/invoices/{inv_id}/pdf")
async def get_invoice_pdf(
    inv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Invoice).where(Invoice.id == inv_id, Invoice.user_id == current_user.id)
    inv = (await db.execute(stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Title (VeriText AI Payment Invoice) >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF"
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Invoice_{inv.order_id}.pdf"'},
    )
