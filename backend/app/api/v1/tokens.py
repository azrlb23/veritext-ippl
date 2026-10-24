"""
Tokens and Billing API Router & Handlers (Phase 6 Hardening)
Provides dedicated /tokens endpoints alongside /billing routes.
"""

from fastapi import APIRouter

from app.api.v1.billing import (
    get_invoice_pdf,
    get_wallet,
    list_invoices,
    midtrans_webhook,
    topup_tokens,
)

create_topup_order = topup_tokens

router = APIRouter(prefix="/tokens", tags=["Tokens & Billing"])

# Map token operations
router.add_api_route("/wallet", get_wallet, methods=["GET"])
router.add_api_route("/topup", topup_tokens, methods=["POST"])
router.add_api_route("/webhook", midtrans_webhook, methods=["POST"])
router.add_api_route("/invoices", list_invoices, methods=["GET"])
router.add_api_route("/invoices/{order_id}/pdf", get_invoice_pdf, methods=["GET"])

__all__ = [
    "router",
    "get_wallet",
    "topup_tokens",
    "create_topup_order",
    "midtrans_webhook",
    "list_invoices",
    "get_invoice_pdf",
]
