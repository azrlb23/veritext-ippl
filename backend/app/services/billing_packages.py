from __future__ import annotations

from fastapi import HTTPException, status

PACKAGES = {
    "pkg_starter": {"name": "Paket Starter", "tokens": 15, "price": 25000},
    "pkg_skripsi_pro": {"name": "Paket Skripsi Pro", "tokens": 50, "price": 65000},
    "pkg_riset_intensif": {"name": "Paket Riset Intensif", "tokens": 150, "price": 150000},
}

UNIT_PACKAGE_ID = "pkg_tokens"
UNIT_PRICE = 2000
UNIT_MIN_TOKENS = 5
UNIT_MAX_TOKENS = 500


def resolve_package(package_id: str, token_amount: int | None = None) -> dict:
    """Mengembalikan {name, tokens, price} untuk paket bundling atau pembelian token satuan (Rp 2.000, minimal 5)."""
    if package_id == UNIT_PACKAGE_ID:
        count = int(token_amount or 0)
        if count < UNIT_MIN_TOKENS or count > UNIT_MAX_TOKENS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pembelian satuan {UNIT_MIN_TOKENS} sampai {UNIT_MAX_TOKENS} token.",
            )
        return {"name": f"Token Satuan ({count} token)", "tokens": count, "price": count * UNIT_PRICE}
    if package_id not in PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package_id. Available: {', '.join([*PACKAGES, UNIT_PACKAGE_ID])}",
        )
    return PACKAGES[package_id]
