from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.models.wallet import TokenWallet
from app.services.document_service import DocumentService
from app.services.upload_charging import estimate_upload


def _file(words: int, name: str = "naskah.txt") -> AsyncMock:
    f = AsyncMock()
    f.filename = name
    f.content_type = "text/plain"
    f.read.return_value = ("ab " * words).encode("utf-8")
    return f


def _db(wallet: TokenWallet) -> MagicMock:
    db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = wallet
    db.execute = AsyncMock(return_value=result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture(autouse=True)
def isolated_upload_dir(tmp_path):
    with patch.object(settings, "UPLOAD_DIR", str(tmp_path)):
        yield tmp_path


async def _upload(db, file, role):
    from app.workers.celery_app import celery_app

    with patch.object(celery_app.control, "inspect", return_value=None):
        return await DocumentService.save_uploaded_file_and_create_task(
            db=db, user_id=uuid.uuid4(), file=file, audit_depth="FULL", user_role=role
        )


async def test_short_document_costs_one_token_regardless_of_depth(isolated_upload_dir):
    wallet = TokenWallet(user_id=uuid.uuid4(), balance=10)
    doc, _ = await _upload(_db(wallet), _file(300), "PREMIUM")
    assert wallet.balance == 9
    assert doc.word_count == 300


async def test_long_document_cost_is_capped_at_five_tokens():
    wallet = TokenWallet(user_id=uuid.uuid4(), balance=20)
    await _upload(_db(wallet), _file(20000), "PREMIUM")
    assert wallet.balance == 15


async def test_free_user_over_2500_words_is_rejected_without_charge_or_leftover_file(isolated_upload_dir):
    wallet = TokenWallet(user_id=uuid.uuid4(), balance=10)
    with pytest.raises(HTTPException) as exc:
        await _upload(_db(wallet), _file(3000), "FREE")
    assert exc.value.status_code == 402
    assert wallet.balance == 10
    assert os.listdir(isolated_upload_dir) == []


async def test_insufficient_balance_rejects_and_removes_stored_file(isolated_upload_dir):
    wallet = TokenWallet(user_id=uuid.uuid4(), balance=1)
    with pytest.raises(HTTPException) as exc:
        await _upload(_db(wallet), _file(6000), "PREMIUM")
    assert exc.value.status_code == 402
    assert wallet.balance == 1
    assert os.listdir(isolated_upload_dir) == []


async def test_estimate_reports_cost_and_plan_without_storing_file(isolated_upload_dir):
    data = await estimate_upload(_file(3000), "FREE")
    assert data == {"word_count": 3000, "token_cost": 2, "within_plan": False, "max_free_words": 2500}
    assert os.listdir(isolated_upload_dir) == []

    data = await estimate_upload(_file(3000), "PREMIUM")
    assert data["within_plan"] is True and data["token_cost"] == 2
