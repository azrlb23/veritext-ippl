from __future__ import annotations

import contextlib
import os

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.wallet import TokenWallet
from app.services.document_validator import write_upload_stream
from app.services.token_pricing import FREE_MAX_WORDS, compute_audit_cost, ensure_within_plan, exceeds_plan_limit
from app.services.word_counter import count_words_in_file

EMPTY_FILE_MESSAGE = "Berkas naskah kosong (0 bytes). Silakan unggah dokumen yang valid."


def remove_stored_file(stored_filename: str) -> None:
    path = os.path.join(settings.UPLOAD_DIR, stored_filename)
    if os.path.exists(path):
        with contextlib.suppress(OSError):
            os.remove(path)


async def stage_upload(file: UploadFile, user_role: str | None) -> tuple[str, int, str, int, int]:
    """Menulis berkas, menghitung kata, dan memvalidasi batas paket. Mengembalikan (nama, ukuran, sha256, kata, biaya)."""
    stored_fn, file_size, sha256 = await write_upload_stream(file, EMPTY_FILE_MESSAGE)
    try:
        words = count_words_in_file(os.path.join(settings.UPLOAD_DIR, stored_fn), file.content_type)
        ensure_within_plan(user_role, words)
    except Exception:
        remove_stored_file(stored_fn)
        raise
    return stored_fn, file_size, sha256, words, compute_audit_cost(words)


async def debit_wallet(db: AsyncSession, user_id, cost: int) -> TokenWallet:
    """Mengunci dompet (SELECT ... FOR UPDATE), memeriksa saldo, lalu memotong token secara atomik."""
    wallet = (await db.execute(select(TokenWallet).where(TokenWallet.user_id == user_id).with_for_update())).scalar_one_or_none()
    if not wallet:
        wallet = TokenWallet(user_id=user_id, balance=0)
        db.add(wallet)
        await db.flush()
    if wallet.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Saldo token tidak mencukupi. Audit ini membutuhkan {cost} token. Saldo Anda: {wallet.balance}",
        )
    wallet.balance -= cost
    return wallet


async def estimate_upload(file: UploadFile, user_role: str | None) -> dict:
    """Menghitung kata dan biaya tanpa menyimpan berkas dan tanpa memotong saldo."""
    stored_fn, _, _, words, cost = await stage_upload(file, None)
    remove_stored_file(stored_fn)
    return {
        "word_count": words,
        "token_cost": cost,
        "within_plan": not exceeds_plan_limit(user_role, words),
        "max_free_words": FREE_MAX_WORDS,
    }
