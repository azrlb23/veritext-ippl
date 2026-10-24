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
    inv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Downloads official token transaction invoice PDF.
    Authorized for invoice owner or ADMIN role (Phase 6 / F5).
    Accepts invoice UUID or Midtrans Order ID.
    """
    inv = None
    try:
        inv_uuid = uuid.UUID(str(inv_id))
        stmt = select(Invoice).where(Invoice.id == inv_uuid)
        inv = (await db.execute(stmt)).scalar_one_or_none()
    except (ValueError, AttributeError):
        pass

    if not inv:
        stmt = select(Invoice).where(Invoice.order_id == str(inv_id))
        inv = (await db.execute(stmt)).scalar_one_or_none()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # Authorization: Caller must be the invoice owner or have ADMIN role
    if getattr(current_user, "role", "") != "ADMIN" and inv.user_id != getattr(current_user, "id", None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this invoice",
        )

    # Resolve buyer information safely
    user_stmt = select(User).where(User.id == inv.user_id)
    buyer = (await db.execute(user_stmt)).scalar_one_or_none()
    if isinstance(buyer, User):
        buyer_name = buyer.full_name or "Pengguna VeriText"
        buyer_email = buyer.email or "user@veritext.ai"
        institution = buyer.institution or "Institut Teknologi Nasional"
    else:
        buyer_name = getattr(current_user, "full_name", "Pengguna VeriText")
        buyer_email = getattr(current_user, "email", "user@veritext.ai")
        institution = getattr(current_user, "institution", "Institut Teknologi Nasional")

    from app.services.pdf_invoice_service import generate_invoice_pdf, clean_invoice_filename

    pdf_bytes = generate_invoice_pdf(
        invoice_id=str(inv.id),
        order_id=inv.order_id,
        user_name=buyer_name,
        user_email=buyer_email,
        institution=institution,
        package_name=inv.package_name,
        token_amount=inv.token_amount,
        gross_amount=float(inv.gross_amount),
        status=inv.status,
        created_at=inv.created_at,
        paid_at=inv.paid_at,
        payment_method=inv.payment_method,
        midtrans_transaction_id=inv.midtrans_transaction_id,
    )

    filename = clean_invoice_filename(inv.order_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

