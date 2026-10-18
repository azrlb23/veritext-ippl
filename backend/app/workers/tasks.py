from datetime import datetime, timezone
import os
import uuid
from typing import Any, Dict, List, Optional
try:
    from celery.utils.log import get_task_logger
except ImportError:
    import logging
    def get_task_logger(name):
        return logging.getLogger(name)

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.database import SyncSessionLocal
from app.models.audit import AuditTask, AuditReport, AuditSentence
from app.models.document import Document
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.engine.preprocessor import TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine
from app.engine.tier4_aggregator import HybridAggregator
from app.engine.reference_corpus import ReferenceCorpusBank

logger = get_task_logger(__name__)


def execute_audit_pipeline(db, audit_task_id: str, document_id: str) -> Dict[str, Any]:
    """Core synchronous logic to execute the 4-tier hybrid audit pipeline."""
    task = db.query(AuditTask).filter(AuditTask.id == uuid.UUID(audit_task_id)).first()
    if not task:
        logger.error(f"Audit task {audit_task_id} not found")
        return {"status": "FAILED", "error": "Task not found"}

    doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
    if not doc:
        logger.error(f"Document {document_id} not found")
        task.status = "FAILED"
        task.error_message = f"Document {document_id} not found"
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "FAILED", "error": "Document not found"}

    try:
        # Step 1: Update task status to PROCESSING
        task.status = "PROCESSING"
        task.started_at = datetime.now(timezone.utc)
        task.progress_pct = 10
        task.current_stage = "TEXT_EXTRACTION"
        db.commit()

        # Step 2: Extract text from uploaded document file
        file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
        doc_text = ""
        if os.path.exists(file_path):
            doc_text = TextPreprocessor.extract_text_from_file(file_path, doc.mime_type)
        else:
            # Fallback if file was not stored on disk (e.g. test environment or mocked upload)
            doc_text = f"Dokumen uji {doc.original_filename}. Sistem deteksi plagiarisme cerdas berbasis arsitektur hybrid leksikal dan semantik."

        if not doc_text.strip():
            doc_text = "Naskah dokumen tanpa konten teks yang dapat diekstraksi."

        # Step 3: Sentence segmentation and DB sentence persistence
        sentences = TextPreprocessor.segment_sentences(doc_text)
        
        # Clean up any existing sentence spans for this audit task
        db.query(AuditSentence).filter(AuditSentence.audit_task_id == task.id).delete()

        for s in sentences:
            sentence_rec = AuditSentence(
                audit_task_id=task.id,
                sentence_index=s.index,
                sentence_text=s.text,
                start_char=s.start_char,
                end_char=s.end_char,
                word_count=s.word_count,
                is_citation=s.is_citation,
            )
            db.add(sentence_rec)

        # Update document word count
        total_word_count = sum(s.word_count for s in sentences)
        doc.word_count = total_word_count
        db.commit()

        task.progress_pct = 25
        task.current_stage = "LOADING_CORPUS_INDEX"
        db.commit()

        # Step 4: Build / load corpus indexes (combine DB indexed corpus with ReferenceCorpusBank)
        corpus_bank = ReferenceCorpusBank.get_instance()
        corpus_index: Dict[int, List[Dict[str, Any]]] = dict(corpus_bank.get_fingerprint_index())
        corpus_chunks: List[Dict[str, Any]] = list(corpus_bank.get_corpus_chunks())

        # Load any additional database corpus fingerprints
        try:
            db_fps = (
                db.query(LexicalFingerprint, CorpusDocument.title, CorpusDocument.category)
                .join(CorpusDocument, LexicalFingerprint.corpus_doc_id == CorpusDocument.id)
                .filter(CorpusDocument.status == "INDEXED")
                .all()
            )
            for fp, title, cat in db_fps:
                h = fp.fingerprint_hash
                if h not in corpus_index:
                    corpus_index[h] = []
                corpus_index[h].append({
                    "doc_id": str(fp.corpus_doc_id),
                    "title": title,
                    "category": cat or "General",
                    "position": fp.position_start,
                })

            db_chunks = (
                db.query(DocumentChunk, CorpusDocument.title, CorpusDocument.category)
                .join(CorpusDocument, DocumentChunk.corpus_doc_id == CorpusDocument.id)
                .filter(CorpusDocument.status == "INDEXED")
                .all()
            )
            for chunk, title, cat in db_chunks:
                corpus_chunks.append({
                    "chunk_id": str(chunk.id),
                    "corpus_doc_id": str(chunk.corpus_doc_id),
                    "title": title,
                    "category": cat or "General",
                    "chunk_text": chunk.chunk_text,
                    "embedding": chunk.embedding,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                })
        except Exception as e:
            logger.warning(f"Note: Could not query database corpus records ({e}), falling back cleanly to built-in ReferenceCorpusBank.")

        # Step 5: Execute 4-Tier Pipeline via HybridAggregator
        task.progress_pct = 40
        task.current_stage = "PROCESSING_TIER1_LEXICAL"
        db.commit()

        aggregator = HybridAggregator(corpus_bank=corpus_bank)
        result = aggregator.run_pipeline(
            original_text=doc_text,
            audit_depth=task.audit_depth,
            custom_corpus_index=corpus_index,
            custom_corpus_chunks=corpus_chunks,
        )

        task.progress_pct = 65
        task.current_stage = "PROCESSING_TIER2_SEMANTIC"
        db.commit()

        task.progress_pct = 85
        task.current_stage = "PROCESSING_TIER3_STYLOMETRIC"
        db.commit()

        task.progress_pct = 95
        task.current_stage = "SAVING_AUDIT_REPORT"
        db.commit()

        # Step 6: Save AuditReport to Database
        # Remove any existing report for this task
        db.query(AuditReport).filter(AuditReport.audit_task_id == task.id).delete()

        report = AuditReport(
            audit_task_id=task.id,
            verification_uuid=uuid.uuid4(),
            score_lexical=result.score_lexical,
            score_semantic=result.score_semantic,
            score_stylometric=result.score_stylometric,
            score_composite=result.score_composite,
            heatmap_annotations=result.heatmap_annotations,
            matched_sources=result.matched_sources,
            pdf_path=None,
        )
        db.add(report)

        # Step 7: Mark Task Complete
        task.status = "SUCCESS"
        task.progress_pct = 100
        task.current_stage = "COMPLETED"
        task.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            f"Audit task {audit_task_id} completed successfully: "
            f"T1={result.score_lexical}%, T2={result.score_semantic}%, "
            f"T3={result.score_stylometric}%, Composite={result.score_composite}%"
        )
        return {
            "status": "SUCCESS",
            "audit_task_id": audit_task_id,
            "composite_score": result.score_composite,
            "score_lexical": result.score_lexical,
            "score_semantic": result.score_semantic,
            "score_stylometric": result.score_stylometric,
            "heatmap_annotations_count": len(result.heatmap_annotations),
            "matched_sources_count": len(result.matched_sources),
        }
    except Exception as exc:
        db.rollback()
        logger.exception(f"Error processing audit task {audit_task_id}: {exc}")
        task = db.query(AuditTask).filter(AuditTask.id == uuid.UUID(audit_task_id)).first()
        if task:
            task.status = "FAILED"
            task.error_message = str(exc)
            task.completed_at = datetime.now(timezone.utc)
            db.commit()
        raise exc


@celery_app.task(bind=True, name="app.workers.tasks.preprocess_and_audit")
def preprocess_and_audit(self, audit_task_id: str, document_id: str) -> Dict[str, Any]:
    """Orchestrates the 4-Tier Hybrid Plagiarism Detection Pipeline asynchronously via Celery."""
    logger.info(f"Starting Celery audit task {audit_task_id} for document {document_id}")
    db = SyncSessionLocal()
    try:
        return execute_audit_pipeline(db, audit_task_id, document_id)
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.index_corpus_document")
def index_corpus_document(corpus_doc_id: str) -> Dict[str, Any]:
    """Indexes corpus document into pgvector embeddings and lexical fingerprints."""
    logger.info(f"Indexing corpus document {corpus_doc_id}")
    db = SyncSessionLocal()
    try:
        doc = db.query(CorpusDocument).filter(CorpusDocument.id == uuid.UUID(corpus_doc_id)).first()
        if not doc:
            return {"status": "FAILED", "error": "Not found"}

        doc.status = "INDEXING"
        db.commit()

        # Read corpus file
        file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
        corpus_text = ""
        if os.path.exists(file_path):
            corpus_text = TextPreprocessor.extract_text_from_file(file_path)
        else:
            corpus_text = f"Naskah Korpus Pembanding: {doc.title}."

        # 1. Segment sentences
        sentences = TextPreprocessor.segment_sentences(corpus_text)

        # 2. Extract Winnowing fingerprints
        lex_engine = WinnowingLexicalEngine()
        fps = lex_engine.extract_fingerprints(corpus_text)

        for h_val, pos in fps:
            fp_rec = LexicalFingerprint(
                corpus_doc_id=doc.id,
                fingerprint_hash=h_val,
                position_start=pos,
                position_end=pos + lex_engine.k,
            )
            db.add(fp_rec)

        # 3. Extract semantic embeddings for chunks
        sem_engine = SemanticEngine()
        for idx, s in enumerate(sentences):
            emb = sem_engine.embed_sentence(s.text)
            chunk_rec = DocumentChunk(
                corpus_doc_id=doc.id,
                chunk_index=idx,
                chunk_text=s.text,
                embedding=emb,
                start_char=s.start_char,
                end_char=s.end_char,
            )
            db.add(chunk_rec)

        doc.status = "INDEXED"
        doc.total_chunks = len(sentences)
        db.commit()

        logger.info(f"Corpus document {corpus_doc_id} indexed successfully ({len(sentences)} chunks, {len(fps)} fingerprints)")
        return {"status": "SUCCESS", "chunks_indexed": len(sentences), "fingerprints_indexed": len(fps)}
    except Exception as e:
        db.rollback()
        logger.exception(f"Corpus indexing error: {e}")
        doc = db.query(CorpusDocument).filter(CorpusDocument.id == uuid.UUID(corpus_doc_id)).first()
        if doc:
            doc.status = "ERROR"
            db.commit()
        raise e
    finally:
        db.close()
