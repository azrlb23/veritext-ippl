from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1 import chat as chat_module
from app.models.wallet import TokenWallet
from app.schemas.chat import ChatMessageRequest
from app.services.chat_context import load_owned_documents, select_relevant_sentences
from app.services.chat_prompt import build_prompt


def test_request_merges_legacy_document_id_and_caps_at_three():
    ids = [uuid.uuid4() for _ in range(3)]
    legacy = uuid.uuid4()
    req = ChatMessageRequest(document_id=legacy, document_ids=ids, prompt="halo")
    assert req.all_document_ids() == ids
    only = ChatMessageRequest(document_id=legacy, prompt="halo")
    assert only.all_document_ids() == [legacy]


def test_prompt_contains_context_history_and_question():
    prompt = build_prompt("Bagaimana memperbaikinya?", "Naskah \"a.txt\":\n- kalimat kunci", [("USER", "tanya awal"), ("ASSISTANT", "jawab awal")])
    assert "kalimat kunci" in prompt
    assert "Pengguna: tanya awal" in prompt and "Asisten: jawab awal" in prompt
    assert prompt.rstrip().endswith("Bagaimana memperbaikinya?")


def test_prompt_without_context_or_history_has_only_instruction_and_question():
    prompt = build_prompt("Apa kabar?", "", [])
    assert "Kutipan naskah" not in prompt and "Percakapan sebelumnya" not in prompt


def test_relevant_sentences_prefer_topic_match_in_document_order():
    sentences = [
        "Resep nasi goreng memerlukan bawang putih dan kecap manis.",
        "Metode penelitian ini memakai survei kuesioner terhadap mahasiswa.",
        "Cuaca hari ini cerah dengan angin sepoi-sepoi di pantai.",
        "Teknik pengambilan sampel penelitian dilakukan secara acak.",
    ]
    picked = select_relevant_sentences("Bagaimana metode penelitian dan sampel?", sentences, top_k=2)
    assert picked == [sentences[1], sentences[3]]


async def test_foreign_or_missing_documents_are_rejected():
    db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result)
    with pytest.raises(HTTPException) as exc:
        await load_owned_documents(db, uuid.uuid4(), [uuid.uuid4()])
    assert exc.value.status_code == 404
    assert await load_owned_documents(db, uuid.uuid4(), []) == []


async def test_send_message_puts_document_context_into_llm_prompt():
    user = SimpleNamespace(id=uuid.uuid4(), role="PREMIUM")
    session = SimpleNamespace(id=uuid.uuid4(), updated_at=None)
    wallet = TokenWallet(user_id=user.id, balance=5, ai_trial_remaining=3)
    db = MagicMock()
    db.add, db.commit, db.refresh = MagicMock(), AsyncMock(), AsyncMock(side_effect=lambda m: setattr(m, "id", uuid.uuid4()))
    gateway = MagicMock()
    gateway.generate_text_with_failover.return_value = ("Saran revisi", "Gemini")
    payload = ChatMessageRequest(document_ids=[uuid.uuid4()], prompt="Perbaiki metode saya")
    with patch.object(chat_module, "_resolve_session", AsyncMock(return_value=(session, [object()], []))), \
         patch.object(chat_module, "build_document_context_async", AsyncMock(return_value="Naskah \"a.txt\":\n- KUTIPAN-RELEVAN")), \
         patch.object(chat_module, "_lock_wallet", AsyncMock(return_value=wallet)), \
         patch.object(chat_module, "DualEngineLLMGateway", return_value=gateway):
        res = await chat_module.send_chat_message(payload, user, db)
    sent_prompt = gateway.generate_text_with_failover.call_args[0][0]
    assert "KUTIPAN-RELEVAN" in sent_prompt and "Perbaiki metode saya" in sent_prompt
    assert res.data.session_id == session.id
    assert res.data.ai_trial_remaining == 2


def test_attach_sentence_ids_matches_annotation_by_char_range():
    from app.services.report_view_helper import attach_sentence_ids

    first = SimpleNamespace(id=uuid.uuid4(), start_char=0, end_char=40)
    second = SimpleNamespace(id=uuid.uuid4(), start_char=41, end_char=90)
    out = attach_sentence_ids([{"start": 41, "end": 90}, {"start": 0, "end": 40}, {"start": 500, "end": 520}], [first, second])
    assert out[0]["sentence_id"] == str(second.id)
    assert out[1]["sentence_id"] == str(first.id)
    assert "sentence_id" not in out[2]
