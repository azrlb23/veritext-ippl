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


AI_UNAVAILABLE = "AI_001: Layanan AI sedang tidak tersedia. Kuota Anda tidak dipotong, coba lagi beberapa saat lagi."


class AssistantService:
    FORBIDDEN_PATTERNS: tuple[str, ...] = (
        "tuliskan skripsi penuh",
        "buatkan skripsi penuh",
        "buatkan bab 1 sampai",
        "palsukan data",
        "manipulasi data penelitian",
        "bikin daftar pustaka palsu",
    )

    @classmethod
    def check_academic_guardrail(cls, prompt: str) -> None:
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="CHAT_001: Pelanggaran Guardrail - Permintaan ini tidak dapat diproses.",
            )
        p_lower = prompt.lower()
        if any(pat in p_lower for pat in cls.FORBIDDEN_PATTERNS):
            raise HTTPException(
                status_code=400,
                detail="CHAT_001: Pelanggaran Guardrail - Permintaan ini tidak dapat diproses.",
            )

    @classmethod
    def consume_ai_quota(
        cls, user: User, wallet: TokenWallet, mode: str = "CHAT"
    ) -> tuple[int, int, int, bool]:
        trial = wallet.ai_trial_remaining or 0
        balance = wallet.balance or 0
        allowance = wallet.ai_chat_allowance_remaining or 0

        if trial > 0:
            wallet.ai_trial_remaining = trial - 1
            return (wallet.ai_trial_remaining, balance, allowance, False)

        role = str(getattr(user, "role", "FREE") or "FREE").upper()
        if role == "FREE":
            raise HTTPException(
                status_code=402,
                detail="CHAT_002: Batas kuota Trial AI Chatbot/Parafrase (3x) untuk Free User telah habis.",
            )

        mode_upper = (mode or "CHAT").upper()
        if mode_upper == "FULL_PAGE":
            if balance < 1:
                raise HTTPException(status_code=402, detail="AUDIT_001: Saldo token tidak mencukupi.")
            wallet.balance = balance - 1
            return (0, wallet.balance, allowance, True)

        if allowance > 0:
            wallet.ai_chat_allowance_remaining = allowance - 1
            return (0, wallet.balance, wallet.ai_chat_allowance_remaining, False)
        if balance < 1:
            raise HTTPException(status_code=402, detail="AUDIT_001: Saldo token tidak mencukupi.")
        wallet.balance = balance - 1
        wallet.ai_chat_allowance_remaining = 9
        return (0, wallet.balance, 9, True)

    @classmethod
    def generate_paraphrase_variations(
        cls, original_text: str, mode: str = "SENTENCE", gateway: DualEngineLLMGateway | None = None
    ) -> tuple[list[dict[str, Any]], str]:
        gw = gateway or DualEngineLLMGateway()
        prompt = (
            f"Parafrasekan teks berikut ({mode}) menjadi 3 variasi gaya akademik.\n"
            "WAJIB pertahankan bahasa yang sama persis dengan teks asli "
            "(jika teks berbahasa Indonesia, seluruh variasi WAJIB berbahasa Indonesia akademik baku; "
            "jangan diterjemahkan ke bahasa lain).\n"
            f"Teks asli:\n{original_text}\n"
            "Format JSON: [{\"option_id\": 1, \"style\": \"Formal\", "
            "\"text\": \"...\", \"predicted_score\": 8.2}, ...]"
        )
        variations: list[dict[str, Any]] = []
        active_engine = "Synthesis Engine"
        try:
            raw_text, engine_name = gw.generate_text_with_failover(prompt)
            if raw_text and engine_name:
                active_engine = engine_name
                cleaned = raw_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                parsed = json.loads(cleaned)
                if isinstance(parsed, list) and len(parsed) >= 3:
                    variations = parsed[:3]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, RuntimeError, OSError, TimeoutError, ConnectionError) as err:
            logger.debug("Gateway paraphrase parsing fallback: %s", err)

        if not variations:
            raise HTTPException(status_code=503, detail=AI_UNAVAILABLE)
        return variations, active_engine

    @classmethod
    def apply_paraphrase_in_place(
        cls,
        sentence: AuditSentence,
        selected_text: str,
        all_sentences: list[AuditSentence],
        report: AuditReport | None = None,
    ) -> dict[str, Any]:
        return apply_paraphrase_update(sentence, selected_text, all_sentences, report)
