from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.llm.gateway import DualEngineLLMGateway
from app.models.audit import AuditReport, AuditSentence
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.chat import (
    ApplyParaphraseRequest,
    ApplyParaphraseResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ParaphraseRequest,
    ParaphraseResponse,
    ParaphraseVariation,
)
from app.schemas.common import APIResponse
from app.services.assistant_service import AssistantService
from app.services.chat_context import build_document_context_async, load_owned_documents
from app.services.chat_prompt import build_prompt
from app.services.chat_sessions import create_session, get_owned_session, recent_history, session_document_ids

router = APIRouter(prefix="/chat", tags=["AI Assistant & Paraphrase"])


async def _lock_wallet(db: AsyncSession, user_id) -> TokenWallet:
    res = await db.execute(select(TokenWallet).where(TokenWallet.user_id == user_id).with_for_update())
    wallet = res.scalar_one_or_none()
    if not wallet:
        wallet = TokenWallet(user_id=user_id, balance=0, ai_trial_remaining=0)
        db.add(wallet)
        await db.flush()
    return wallet


async def _resolve_session(db: AsyncSession, user_id, payload: ChatMessageRequest):
    """Menentukan sesi (lama atau baru), naskah konteksnya, dan riwayat singkat."""
    if payload.session_id:
        session = await get_owned_session(db, user_id, payload.session_id)
        doc_ids = await session_document_ids(db, session.id)
        return session, await load_owned_documents(db, user_id, doc_ids), await recent_history(db, session.id)
    doc_ids = payload.all_document_ids()
    docs = await load_owned_documents(db, user_id, doc_ids)
    session = await create_session(db, user_id, doc_ids, payload.prompt)
    return session, docs, []


@router.post("/message", response_model=APIResponse[ChatMessageResponse])
async def send_chat_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    AssistantService.check_academic_guardrail(payload.prompt)
    session, docs, history = await _resolve_session(db, current_user.id, payload)
    context = await build_document_context_async(docs, payload.prompt)
    wallet = await _lock_wallet(db, current_user.id)
    trial_rem, bal, allow_rem, token_ded = AssistantService.consume_ai_quota(current_user, wallet, mode="CHAT")
    if token_ded:
        db.add(TokenTransaction(
            wallet_id=wallet.id, transaction_type="DEBIT_CHAT_PARAPHRASE", amount=-1,
            balance_after=wallet.balance, reference_id=session.id, note="AI Chatbot token debit",
        ))

    db.add(ChatMessage(session_id=session.id, role="USER", content=payload.prompt, target_sentence_id=payload.sentence_id))
    ai_text, engine = DualEngineLLMGateway().generate_text_with_failover(build_prompt(payload.prompt, context, history))
    assistant_msg = ChatMessage(
        session_id=session.id, role="ASSISTANT",
        content=ai_text or "Disarankan merevisi struktur kalimat untuk menjaga orisinalitas naskah.",
        mode="CONSULTATION", target_sentence_id=payload.sentence_id,
    )
    db.add(assistant_msg)
    session.updated_at = func.now()
    await db.commit()
    await db.refresh(assistant_msg)

    return APIResponse(data=ChatMessageResponse(
        message_id=assistant_msg.id, session_id=session.id, role="ASSISTANT",
        content=assistant_msg.content, active_engine=engine or "Synthesis Engine",
        ai_trial_remaining=trial_rem, balance=bal, ai_chat_allowance_remaining=allow_rem,
    ))


@router.post("/paraphrase", response_model=APIResponse[ParaphraseResponse])
async def paraphrase_sentence(
    payload: ParaphraseRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    sentence = await db.get(AuditSentence, payload.sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    wallet = await _lock_wallet(db, current_user.id)
    _, _, _, token_ded = AssistantService.consume_ai_quota(current_user, wallet, mode=payload.mode)
    if token_ded:
        db.add(TokenTransaction(
            wallet_id=wallet.id, transaction_type="DEBIT_CHAT_PARAPHRASE", amount=-1,
            balance_after=wallet.balance, reference_id=sentence.id, note=f"Paraphrase {payload.mode} token debit",
        ))

    variations, active_engine = AssistantService.generate_paraphrase_variations(
        sentence.current_text or sentence.sentence_text, mode=payload.mode
    )
    await db.commit()
    return APIResponse(data=ParaphraseResponse(
        sentence_id=payload.sentence_id, mode=payload.mode,
        variations=[ParaphraseVariation(**v) for v in variations], active_engine=active_engine,
    ))


@router.post("/apply-paraphrase", response_model=APIResponse[ApplyParaphraseResponse])
async def apply_paraphrase(
    payload: ApplyParaphraseRequest,
    _current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    sentence = await db.get(AuditSentence, payload.sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    all_s = (await db.execute(select(AuditSentence).where(AuditSentence.audit_task_id == sentence.audit_task_id))).scalars().all()
    report = (await db.execute(select(AuditReport).where(AuditReport.audit_task_id == sentence.audit_task_id))).scalar_one_or_none()
    result = AssistantService.apply_paraphrase_in_place(sentence, payload.selected_text, list(all_s), report)
    await db.commit()
    return APIResponse(data=ApplyParaphraseResponse(**result))
