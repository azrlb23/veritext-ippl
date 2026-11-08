from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime
from typing import Any

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc  # noqa: UP017

from app.core.config import settings
from app.core.database import SyncSessionLocal
from app.engine.corpus_ann import PgvectorChunkSearch
from app.engine.preprocessor import TextPreprocessor
from app.engine.reference_corpus import ReferenceCorpusBank
from app.engine.tier4_aggregator import HybridAggregator
from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.document import Document
from app.workers.celery_app import celery_app
from app.workers.task_helpers import (
    clean_zombie_tasks,
    handle_audit_failure,
    handle_web_scan_refund,
    load_corpus_indexes,
)

logger = logging.getLogger(__name__)


def execute_audit_pipeline(db: Any, audit_task_id: str, document_id: str) -> dict[str, Any]:
    task = db.query(AuditTask).filter(AuditTask.id == uuid.UUID(audit_task_id)).first()
    if not task:
        logger.error("Audit task %s not found", audit_task_id)
        return {"status": "FAILED", "error": "Task not found"}

    doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
    if not doc:
        logger.error("Document %s not found", document_id)
        task.status, task.error_message, task.completed_at = "FAILED", f"Document {document_id} not found", datetime.now(UTC)
        db.commit()
        return {"status": "FAILED", "error": "Document not found"}

    try:
        task.status, task.started_at, task.progress_pct = "PROCESSING", datetime.now(UTC), 15
        task.current_stage = "Tahap 1 · Ekstraksi struktur teks & segmentasi kalimat"
        db.commit()

        file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
        doc_text = TextPreprocessor.extract_text_from_file(file_path, doc.mime_type) if os.path.exists(file_path) else (
            f"Dokumen uji {doc.original_filename}. Sistem deteksi plagiarisme cerdas berbasis arsitektur hybrid leksikal dan semantik."
        )
        doc_text = doc_text.strip() or "Naskah dokumen tanpa konten teks yang dapat diekstraksi."

        sentences = TextPreprocessor.segment_sentences(doc_text)
        db.query(AuditSentence).filter(AuditSentence.audit_task_id == task.id).delete()
        for s in sentences:
            db.add(AuditSentence(
                audit_task_id=task.id, sentence_index=s.index, sentence_text=s.text,
                start_char=s.start_char, end_char=s.end_char, word_count=s.word_count, is_citation=s.is_citation,
            ))
        doc.word_count = sum(s.word_count for s in sentences)
        task.progress_pct, task.current_stage = 25, "LOADING_CORPUS_INDEX"
        db.commit()

        corpus_bank = ReferenceCorpusBank.get_instance()
        corpus_index, corpus_chunks = load_corpus_indexes(db, corpus_bank, logger)
        task.progress_pct, task.current_stage = 40, "Tahap 2 · Penelusuran internet & korpus"
        db.commit()

        def update_progress(pct: int, stage_text: str):
            try:
                task.progress_pct, task.current_stage = pct, stage_text
                db.commit()
            except Exception as err:  # noqa: BLE001
                logger.debug("Progress update skipped: %s", err)

        aggregator = HybridAggregator(corpus_bank=corpus_bank)
        result = aggregator.run_pipeline(
            original_text=doc_text, audit_depth=task.audit_depth,
            custom_corpus_index=corpus_index, custom_corpus_chunks=corpus_chunks,
            on_progress=update_progress, corpus_searcher=PgvectorChunkSearch(db),
        )

        handle_web_scan_refund(db, task, result, logger)
        task.progress_pct, task.current_stage = 95, "SAVING_AUDIT_REPORT"
        db.commit()

        db.query(AuditReport).filter(AuditReport.audit_task_id == task.id).delete()
        db.add(AuditReport(
            audit_task_id=task.id, verification_uuid=uuid.uuid4(),
            score_lexical=result.score_lexical, score_semantic=result.score_semantic,
            score_stylometric=result.score_stylometric, score_composite=result.score_composite,
            heatmap_annotations=result.heatmap_annotations, matched_sources=result.matched_sources,
        ))

        task.status, task.progress_pct, task.current_stage, task.completed_at = "SUCCESS", 100, "COMPLETED", datetime.now(UTC)
        db.commit()

        logger.info("Audit task %s completed: Composite=%s%%", audit_task_id, result.score_composite)
        return {
            "status": "SUCCESS", "audit_task_id": audit_task_id, "composite_score": result.score_composite,
            "score_lexical": result.score_lexical, "score_semantic": result.score_semantic,
            "score_stylometric": result.score_stylometric,
            "heatmap_annotations_count": len(result.heatmap_annotations),
            "matched_sources_count": len(result.matched_sources),
        }
    except Exception as exc:
        db.rollback()
        logger.exception("Error processing audit task %s", audit_task_id)
        handle_audit_failure(db, audit_task_id, exc, logger)
        raise


@celery_app.task(bind=True, name="app.workers.tasks.preprocess_and_audit")
def preprocess_and_audit(self, audit_task_id: str, document_id: str) -> dict[str, Any]:
    logger.info("Starting Celery audit task %s for doc %s", audit_task_id, document_id)
    with SyncSessionLocal() as db:
        return execute_audit_pipeline(db, audit_task_id, document_id)


run_plagiarism_audit = preprocess_and_audit




@celery_app.task(name="app.workers.tasks.reap_zombie_tasks")
def reap_zombie_tasks() -> dict[str, Any]:
    with SyncSessionLocal() as db:
        return {"status": "SUCCESS", "reaped_tasks": clean_zombie_tasks(db, threshold_minutes=30)}
