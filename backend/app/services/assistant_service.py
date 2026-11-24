from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import HTTPException

from app.llm.gateway import DualEngineLLMGateway
from app.models.audit import AuditReport, AuditSentence
from app.models.user import User
from app.models.wallet import TokenWallet
from app.services.paraphrase_helper import apply_paraphrase_update

logger = logging.getLogger(__name__)
_PARAPHRASE_MODES = ("SENTENCE", "PARAGRAPH", "FULL_PAGE")
_PREMIUM_DETAIL = "PREMIUM_REQUIRED: Fitur parafrase hanya tersedia untuk akun Premium."
_GUARDRAIL_DETAIL = "CHAT_001: Pelanggaran Guardrail - Permintaan ini tidak dapat diproses."
_TRIAL_DETAIL = "CHAT_002: Batas kuota Trial AI Chatbot/Parafrase (3x) untuk Free User telah habis."
_TOKEN_DETAIL = "AUDIT_001: Saldo token tidak mencukupi."
AI_UNAVAILABLE = "AI_001: Layanan AI sedang tidak tersedia. Kuota Anda tidak dipotong, coba lagi beberapa saat lagi."


def _try_local_paraphrase(original_text: str) -> tuple[list[dict[str, Any]], str]:
    try:
        from app.llm.local_paraphraser import generate_local_paraphrases

        local_vars = generate_local_paraphrases(original_text, count=3)
        if isinstance(local_vars, list) and local_vars:
            return local_vars[:3], "Transformers (Local)"
    except (ImportError, RuntimeError, OSError, ValueError, TypeError) as err:
        logger.debug("Local paraphraser fallback unavailable: %s", err)
    return [], ""


class AssistantService:
    FORBIDDEN_PATTERNS: tuple[str, ...] = (
        "tuliskan skripsi penuh", "buatkan skripsi penuh", "buatkan bab 1 sampai",
        "palsukan data", "manipulasi data penelitian", "bikin daftar pustaka palsu",
        "buatkan makalah", "buatkan laporan lengkap", "kerjakan tugas", "jawabkan soal",
    )

    @classmethod
    def check_academic_guardrail(cls, prompt: str) -> None:
        if not prompt or not prompt.strip():
            raise HTTPException(status_code=400, detail=_GUARDRAIL_DETAIL)
        p_lower = prompt.lower()
        if any(pat in p_lower for pat in cls.FORBIDDEN_PATTERNS):
            raise HTTPException(status_code=400, detail=_GUARDRAIL_DETAIL)

    @classmethod
    def check_ai_quota_available(cls, user: User, wallet: TokenWallet | None, mode: str = "CHAT") -> None:
        mode_upper = (mode or "CHAT").upper()
        role = str(getattr(user, "role", "FREE") or "FREE").upper()
        if mode_upper in _PARAPHRASE_MODES and role == "FREE":
            raise HTTPException(status_code=403, detail=_PREMIUM_DETAIL)
        if ((wallet.ai_trial_remaining or 0) if wallet else 0) > 0:
            return
        if role == "FREE":
            raise HTTPException(status_code=402, detail=_TRIAL_DETAIL)
        balance = (wallet.balance or 0) if wallet else 0
        allowance = (wallet.ai_chat_allowance_remaining or 0) if wallet else 0
        if (mode_upper == "FULL_PAGE" and balance < 1) or (allowance <= 0 and balance < 1):
            raise HTTPException(status_code=402, detail=_TOKEN_DETAIL)

    @classmethod
    def consume_ai_quota(cls, user: User, wallet: TokenWallet, mode: str = "CHAT") -> tuple[int, int, int, bool]:
        mode_upper = (mode or "CHAT").upper()
        role = str(getattr(user, "role", "FREE") or "FREE").upper()
        if mode_upper in _PARAPHRASE_MODES and role == "FREE":
            raise HTTPException(status_code=403, detail=_PREMIUM_DETAIL)
        trial, balance, allowance = wallet.ai_trial_remaining or 0, wallet.balance or 0, wallet.ai_chat_allowance_remaining or 0
        if trial > 0:
            wallet.ai_trial_remaining = trial - 1
            return (wallet.ai_trial_remaining, balance, allowance, False)
        if role == "FREE":
            raise HTTPException(status_code=402, detail=_TRIAL_DETAIL)
        if mode_upper == "FULL_PAGE":
            if balance < 1:
                raise HTTPException(status_code=402, detail=_TOKEN_DETAIL)
            wallet.balance = balance - 1
            return (0, wallet.balance, allowance, True)
        if allowance > 0:
            wallet.ai_chat_allowance_remaining = allowance - 1
            return (0, wallet.balance, wallet.ai_chat_allowance_remaining, False)
        if balance < 1:
            raise HTTPException(status_code=402, detail=_TOKEN_DETAIL)
        wallet.balance, wallet.ai_chat_allowance_remaining = balance - 1, 9
        return (0, wallet.balance, 9, True)

    @classmethod
    def generate_paraphrase_variations(
        cls, original_text: str, mode: str = "SENTENCE",
        gateway: DualEngineLLMGateway | None = None, preferred_engine: str = "auto",
    ) -> tuple[list[dict[str, Any]], str]:
        if (preferred_engine or "").strip().lower() == "transformers":
            variations, active_engine = _try_local_paraphrase(original_text)
            if not variations:
                raise HTTPException(status_code=503, detail=AI_UNAVAILABLE)
            return variations, active_engine
        gw = gateway or DualEngineLLMGateway()
        prompt = (
            f"Parafrasekan teks berikut ({mode}) menjadi 3 variasi gaya akademik.\n"
            "WAJIB pertahankan bahasa yang sama persis dengan teks asli "
            "(jika teks berbahasa Indonesia, seluruh variasi WAJIB berbahasa Indonesia akademik baku; "
            "jangan diterjemahkan ke bahasa lain).\n"
            f"Teks asli:\n{original_text}\n"
            "KEMBALIKAN HANYA JSON ARRAY MURNI (diawali `[` dan diakhiri `]`) tanpa teks pengantar atau markdown:\n"
            '[{"option_id": 1, "style": "Formal", "text": "...", "predicted_score": 8.2}, ...]'
        )
        variations: list[dict[str, Any]] = []
        active_engine = "Synthesis Engine"
        try:
            raw_text, engine_name = gw.generate_text_with_failover(prompt, preferred_engine=preferred_engine)
            if raw_text and engine_name:
                active_engine = engine_name
                cleaned = raw_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                start_i, end_i = cleaned.find("["), cleaned.rfind("]")
                if start_i != -1 and end_i > start_i:
                    cleaned = cleaned[start_i : end_i + 1]
                parsed = json.loads(cleaned)
                if isinstance(parsed, list) and len(parsed) >= 3:
                    variations = parsed[:3]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, RuntimeError, OSError, TimeoutError, ConnectionError) as err:
            logger.debug("Gateway paraphrase parsing fallback: %s", err)

        if not variations:
            variations, local_engine = _try_local_paraphrase(original_text)
            if local_engine:
                active_engine = local_engine

        if not variations:
            raise HTTPException(status_code=503, detail=AI_UNAVAILABLE)
        return variations, active_engine

    @classmethod
    def apply_paraphrase_in_place(
        cls, sentence: AuditSentence, selected_text: str,
        all_sentences: list[AuditSentence], report: AuditReport | None = None,
    ) -> dict[str, Any]:
        return apply_paraphrase_update(sentence, selected_text, all_sentences, report)
