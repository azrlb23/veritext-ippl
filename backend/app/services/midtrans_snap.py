from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)
SANDBOX_URL = "https://app.sandbox.midtrans.com/snap/v1/transactions"
PRODUCTION_URL = "https://app.midtrans.com/snap/v1/transactions"


def snap_enabled() -> bool:
    """Snap aktif hanya bila kunci server asli terisi (bukan kunci contoh bawaan)."""
    key = (settings.MIDTRANS_SERVER_KEY or "").strip()
    return bool(key) and "DemoServerKey" not in key


def client_key() -> str | None:
    return settings.MIDTRANS_CLIENT_KEY if snap_enabled() else None


async def create_snap_token(order_id: str, gross_amount: int, item_name: str, token_amount: int, customer: dict) -> str | None:
    """Membuat transaksi Snap di Midtrans dan mengembalikan token pembayaran; None bila nonaktif atau gagal."""
    if not snap_enabled():
        return None
    payload = {
        "transaction_details": {"order_id": order_id, "gross_amount": gross_amount},
        "item_details": [{"id": order_id, "price": gross_amount, "quantity": 1, "name": item_name[:50]}],
        "customer_details": customer,
        "callbacks": {"finish": f"{settings.FRONTEND_URL.rstrip('/')}/billing"},
    }
    url = PRODUCTION_URL if settings.MIDTRANS_IS_PRODUCTION else SANDBOX_URL
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload, auth=(settings.MIDTRANS_SERVER_KEY, ""))
        res.raise_for_status()
        return res.json().get("token")
    except (httpx.HTTPError, ValueError) as err:
        logger.warning("Pembuatan token Snap gagal untuk %s: %s", order_id, err)
        return None
