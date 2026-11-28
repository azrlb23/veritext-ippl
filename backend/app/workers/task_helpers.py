from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc  # noqa: UP017

from sqlalchemy import and_, or_

from app.models.audit import AuditTask
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.models.wallet import TokenTransaction, TokenWallet


def load_corpus_indexes(
    db: Any, corpus_bank: Any, logger: Any, doc_text: str | None = None
) -> tuple[dict[int, list[dict[str, Any]]], list[dict[str, Any]]]:
    corpus_index: dict[int, list[dict[str, Any]]] = dict(corpus_bank.get_fingerprint_index())
    # Potongan korpus basis data dicari lewat indeks HNSW pgvector (lihat PgvectorChunkSearch), bukan dimuat ke memori.
    corpus_chunks: list[dict[str, Any]] = list(corpus_bank.get_corpus_chunks())
    try:
        q_base = (
            db.query(
                LexicalFingerprint.fingerprint_hash,
                LexicalFingerprint.corpus_doc_id,
                LexicalFingerprint.position_start,
                CorpusDocument.title,
                CorpusDocument.category,
            )
            .join(CorpusDocument, LexicalFingerprint.corpus_doc_id == CorpusDocument.id)
            .filter(CorpusDocument.status == "INDEXED")
        )
        if doc_text:
            doc_hashes = list({h for h, _ in corpus_bank.lexical_engine.extract_fingerprints(doc_text)})
            raw_rows = []
            for i in range(0, len(doc_hashes), 4000):
                raw_rows.extend(q_base.filter(LexicalFingerprint.fingerprint_hash.in_(doc_hashes[i : i + 4000])).all())
            hash_docs: dict[int, set[str]] = {}
            for fp_hash, doc_id, *_ in raw_rows:
                hash_docs.setdefault(fp_hash, set()).add(str(doc_id))
            rows = [r for r in raw_rows if len(hash_docs.get(r[0], ())) <= 50]
            cand_ids = list({r[1] for r in rows})
            doc_texts: dict[Any, str] = {}
            for i in range(0, len(cand_ids), 200):
                chunk_rows = (
                    db.query(DocumentChunk.corpus_doc_id, DocumentChunk.chunk_text)
                    .filter(DocumentChunk.corpus_doc_id.in_(cand_ids[i : i + 200]))
                    .order_by(DocumentChunk.chunk_index.asc())
                    .all()
                )
                for cid, ctxt in chunk_rows:
                    if ctxt:
                        doc_texts[cid] = (doc_texts.get(cid, "") + " " + ctxt).strip()
        else:
            rows = q_base.yield_per(5000)
            doc_texts = {}
        for fp_hash, doc_id, pos_start, title, cat in rows:
            corpus_index.setdefault(fp_hash, []).append({
                "doc_id": str(doc_id), "title": title,
                "category": cat or "General", "position": pos_start,
                "snippet": doc_texts.get(doc_id, ""),
            })
    except Exception as e:  # noqa: BLE001
        logger.warning("Database corpus query fallback to ReferenceCorpusBank: %s", e)
    return corpus_index, corpus_chunks


def _refund_audit_debit(db: Any, task: Any, note: str) -> None:
    if not task.user_id:
        return
    db.query(AuditTask).filter(AuditTask.id == task.id).with_for_update().first()
    wallet = db.query(TokenWallet).filter(TokenWallet.user_id == task.user_id).with_for_update().first()
    if not wallet:
        return
    debit = db.query(TokenTransaction).filter(
        TokenTransaction.reference_id == task.id, TokenTransaction.transaction_type == "DEBIT_AUDIT"
    ).first()
    already = db.query(TokenTransaction).filter(
        TokenTransaction.reference_id == task.id, TokenTransaction.transaction_type == "CREDIT_REFUND"
    ).first()
    if debit and not already:
        wallet.balance += abs(debit.amount)
        db.add(TokenTransaction(
            wallet_id=wallet.id, transaction_type="CREDIT_REFUND", amount=abs(debit.amount),
            balance_after=wallet.balance, reference_id=task.id, note=note,
        ))


def handle_web_scan_refund(db: Any, task: AuditTask, result: Any, logger: Any) -> None:
    if task.audit_depth != "FULL" or getattr(result, "web_scan_available", True) or not task.user_id:
        return
    try:
        already = db.query(TokenTransaction).filter(
            TokenTransaction.reference_id == task.id,
            TokenTransaction.transaction_type.in_(["CREDIT_REFUND", "REFUND"]),
        ).first()
        if not already and (wallet := db.query(TokenWallet).filter(TokenWallet.user_id == task.user_id).with_for_update().first()):
            wallet.balance += 1
            db.add(TokenTransaction(
                wallet_id=wallet.id, transaction_type="CREDIT_REFUND", amount=1,
                balance_after=wallet.balance, reference_id=task.id,
                note="Pengembalian 1 token: pemindaian web tidak tersedia",
            ))
            task.error_message = getattr(result, "web_scan_note", "Pemindaian web tidak tersedia (1 token dikembalikan)")
            logger.info("Task %s: 1 token refunded because web scan was unavailable.", task.id)
    except Exception as ref_err:  # noqa: BLE001
        logger.warning("Gagal memproses refund 1 token: %s", ref_err)


def handle_audit_failure(db: Any, audit_task_id: str, exc: Exception, logger: Any) -> None:
    task = db.query(AuditTask).filter(AuditTask.id == uuid.UUID(audit_task_id)).first()
    if not task:
        return
    task.status, task.error_message, task.completed_at = "FAILED", str(exc), datetime.now(UTC)
    try:
        _refund_audit_debit(db, task, f"Automatic refund for failed audit task {task.id}")
    except Exception as refund_err:  # noqa: BLE001
        logger.error("Failed to process auto-refund on task error: %s", refund_err)
    db.commit()


def clean_zombie_tasks(db: Any, threshold_minutes: int = 30) -> int:
    cutoff = datetime.now(UTC) - timedelta(minutes=threshold_minutes)
    zombie_tasks = (
        db.query(AuditTask)
        .filter(AuditTask.status == "PROCESSING", or_(AuditTask.started_at < cutoff, and_(AuditTask.started_at.is_(None), AuditTask.created_at < cutoff)))
        .all()
    )
    for task in zombie_tasks:
        task.status = "FAILED"
        task.error_message = f"Task execution timed out after exceeding {threshold_minutes} minutes"
        task.completed_at = datetime.now(UTC)
        _refund_audit_debit(db, task, f"Automatic refund for timed out audit task {task.id}")
    if zombie_tasks:
        db.commit()
    return len(zombie_tasks)
