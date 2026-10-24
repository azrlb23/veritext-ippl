"""
Test Suite: Remediation Phase 5 — Ketahanan Engine AI, Visualisasi Heatmap & Frontend Error Boundaries
TDD Tests verifying:
  - test_tc_sec_30_dto_includes_document_text
  - test_tc_sec_31_engine_nan_inf_score_sanitization
  - test_tc_sec_32_pytorch_inference_mode_singleton
  - test_tc_sec_33_safe_zip_decompression_anti_bomb_slip
"""

import asyncio
from datetime import datetime, timezone
import io
import math
import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import zipfile

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditTask, AuditReport, AuditSentence
from app.schemas.audit import AuditReportResponse
from app.engine.tier4_aggregator import HybridAggregator
from app.engine.tier2_semantic import SemanticEngine
from app.services.corpus_service import CorpusService


class MockQueryResult:
    def __init__(self, items=None, scalar_val=None):
        self._items = items if items is not None else []
        self._scalar_val = scalar_val

    def scalar_one_or_none(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalar(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None


class MockAsyncSession:
    def __init__(self, execute_handler=None):
        self.execute_handler = execute_handler
        self.executed_statements = []

    async def execute(self, stmt):
        self.executed_statements.append(stmt)
        if self.execute_handler:
            res = self.execute_handler(stmt)
            if asyncio.iscoroutine(res):
                return await res
            return res
        return MockQueryResult([])


class TestRemediationPhase5(unittest.IsolatedAsyncioTestCase):
    """
    Test Suite Fase 5:
    Ketahanan Engine AI, Visualisasi Heatmap & Frontend Error Boundaries
    """

    async def test_tc_sec_30_dto_includes_document_text(self):
        """
        [C4 & DTO] Skema AuditReportResponse Memuat Field 'document_text' yang Dinamis.
        - Memastikan field document_text ada di AuditReportResponse (Optional[str]).
        - Model validation mengekstrak teks naskah dari AuditReport / AuditSentence / storage.
        - Endpoint /reports/{id} mengembalikan document_text sehingga frontend HeatmapViewer
          dapat merender naskah pengguna asli secara dinamis.
        """
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            full_name="Mahasiswa Skripsi",
            email="mahasiswa@kampus.ac.id",
            role="TRIAL",
            is_active=True,
        )

        doc = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            original_filename="Tugas_Akhir_Komparasi.docx",
            stored_filename="ta_komparasi_stored.docx",
            file_size_bytes=1024,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            status="READY",
        )

        task = AuditTask(
            id=uuid.uuid4(),
            document_id=doc.id,
            user_id=user_id,
            document=doc,
            user=user,
            status="SUCCESS",
            progress_pct=100,
        )

        sentence1 = AuditSentence(
            id=uuid.uuid4(),
            audit_task_id=task.id,
            sentence_index=0,
            sentence_text="Kecerdasan buatan telah berkembang pesat dalam dunia riset modern.",
            start_char=0,
            end_char=66,
            word_count=9,
        )
        sentence2 = AuditSentence(
            id=uuid.uuid4(),
            audit_task_id=task.id,
            sentence_index=1,
            sentence_text="Deteksi plagiarisme membutuhkan pendekatan hybrid antara leksikal dan semantik.",
            start_char=67,
            end_char=146,
            word_count=10,
        )
        task.sentences = [sentence1, sentence2]

        report_id = uuid.uuid4()
        report = AuditReport(
            id=report_id,
            audit_task_id=task.id,
            audit_task=task,
            verification_uuid=uuid.uuid4(),
            score_lexical=12.5,
            score_semantic=15.0,
            score_stylometric=5.0,
            score_composite=11.5,
            heatmap_annotations=[],
            matched_sources=[],
            generated_at=datetime.now(timezone.utc),
        )

        # 1. Pydantic schema validation check
        dto = AuditReportResponse.model_validate(report)
        self.assertTrue(hasattr(dto, "document_text"))
        self.assertIsNotNone(dto.document_text)
        self.assertIn("Kecerdasan buatan telah berkembang pesat", dto.document_text)
        self.assertIn("Deteksi plagiarisme membutuhkan pendekatan hybrid", dto.document_text)

        # 2. Endpoint integration check via get_report
        from app.api.v1 import reports as report_router
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([report]))
        resp = await report_router.get_report(
            report_id=report_id,
            current_user=user,
            db=mock_db,
        )
        self.assertEqual(resp.data.id, report_id)
        self.assertIsNotNone(resp.data.document_text)
        self.assertIn("Kecerdasan buatan", resp.data.document_text)

    def test_tc_sec_31_engine_nan_inf_score_sanitization(self):
        """
        [ROBUSTNESS] Sanitasi Nilai NaN & Inf pada Mesin Agregasi Tier 4.
        - Memastikan math.isnan() dan math.isinf() pada masukan skor tidak memicu crash,
          menghasilkan NaN pada JSON response, atau merusak kalkulasi bobot.
        - Skor yang tidak valid (NaN/Inf/-Inf/None) dinormalisasi secara aman ke rentang 0.0 s/d 100.0.
        """
        aggregator = HybridAggregator()

        # Kasus A: Skor T1 NaN, T2 dan T3 valid
        score_a = aggregator.calculate_composite_score(float("nan"), 50.0, 10.0)
        self.assertFalse(math.isnan(score_a))
        self.assertFalse(math.isinf(score_a))
        self.assertGreaterEqual(score_a, 0.0)
        self.assertLessEqual(score_a, 100.0)

        # Kasus B: Skor Inf dan -Inf
        score_b = aggregator.calculate_composite_score(float("inf"), 20.0, float("-inf"))
        self.assertFalse(math.isnan(score_b))
        self.assertFalse(math.isinf(score_b))
        self.assertGreaterEqual(score_b, 0.0)
        self.assertLessEqual(score_b, 100.0)

        # Kasus C: Semua input NaN
        score_c = aggregator.calculate_composite_score(float("nan"), float("nan"), float("nan"))
        self.assertEqual(score_c, 0.0)

        # Kasus D: Nilai normal tetap terhitung presisi
        # Default weight: w_lexical=0.50, w_semantic=0.35, w_stylometric=0.15
        # 0.50 * 40.0 + 0.35 * 60.0 + 0.15 * 10.0 = 20.0 + 21.0 + 1.5 = 42.5
        score_d = aggregator.calculate_composite_score(40.0, 60.0, 10.0)
        self.assertEqual(score_d, 42.5)

    def test_tc_sec_32_pytorch_inference_mode_singleton(self):
        """
        [RAM LEAK PREVENTION] Singleton Model Pattern & torch.inference_mode.
        - Memastikan pemuatan model transformer menggunakan pola Singleton (satu instance bersama).
        - Ekstraksi vektor semantik dibungkus dalam torch.inference_mode() atau torch.no_grad()
          sehingga autograd computation graph tidak terbentuk dan tidak menumpuk di RAM server.
        """
        engine1 = SemanticEngine()
        engine2 = SemanticEngine()

        # 1. Singleton pattern check: class level / shared instance
        # Mock transformer model loader
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)

        with patch("app.engine.tier2_semantic.SemanticEngine.get_shared_model", return_value=mock_model):
            emb1 = engine1.embed_sentence("Kalimat uji satu.")
            emb2 = engine2.embed_sentence("Kalimat uji dua.")
            self.assertEqual(len(emb1), 384)
            self.assertEqual(len(emb2), 384)

        # 2. Inference mode check: test wrapping with torch.inference_mode or torch.no_grad
        import sys
        if "torch" in sys.modules or True:
            # Test that inference wrapper correctly invokes torch inference context if available
            with patch("app.engine.tier2_semantic.get_inference_context") as mock_ctx:
                mock_context_manager = MagicMock()
                mock_ctx.return_value = mock_context_manager
                mock_context_manager.__enter__.return_value = None

                engine = SemanticEngine()
                engine._transformer_model = mock_model
                res = engine.embed_sentence("Pengujian inference context")
                self.assertEqual(len(res), 384)
                mock_context_manager.__enter__.assert_called_once()
                mock_context_manager.__exit__.assert_called_once()

    def test_tc_sec_33_safe_zip_decompression_anti_bomb_slip(self):
        """
        [SECURITY] Safe ZIP Decompression Anti Zip-Slip & Anti Zip-Bomb.
        - Memvalidasi os.path.abspath terhadap direktori tujuan ekstraksi (mencegah directory traversal / zip slip).
        - Memvalidasi total uncompressed bytes (maksimum ambang batas 200MB, mencegah zip bomb DoS).
        - Ekstraksi arsip ZIP valid berhasil tanpa error.
        """
        with tempfile.TemporaryDirectory() as extract_dir:
            # 1. Kasus A: Serangan Zip-Slip (File traversal "../../malicious.txt")
            zip_buffer_slip = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_slip, "w") as zf:
                zf.writestr("../../slip_attack.txt", "isi berbahaya di luar direktori")
            zip_buffer_slip.seek(0)

            with self.assertRaises(HTTPException) as ctx_slip:
                CorpusService.extract_zip_safely(
                    zip_file=zip_buffer_slip,
                    target_dir=extract_dir,
                    max_uncompressed_bytes=200 * 1024 * 1024,
                )
            self.assertEqual(ctx_slip.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertTrue(
                "slip" in ctx_slip.exception.detail.lower()
                or "traversal" in ctx_slip.exception.detail.lower()
                or "invalid path" in ctx_slip.exception.detail.lower(),
                f"Detail must indicate path traversal: {ctx_slip.exception.detail}",
            )

            # 2. Kasus B: Serangan Zip-Bomb (Ukuran dekompresi melebihi ambang batas)
            zip_buffer_bomb = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_bomb, "w") as zf:
                zf.writestr("large_payload.txt", b"x" * 2048)
            zip_buffer_bomb.seek(0)

            with self.assertRaises(HTTPException) as ctx_bomb:
                CorpusService.extract_zip_safely(
                    zip_file=zip_buffer_bomb,
                    target_dir=extract_dir,
                    max_uncompressed_bytes=1024,  # Threshold 1024 < 2048 bytes
                )
            self.assertEqual(ctx_bomb.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertTrue(
                "bomb" in ctx_bomb.exception.detail.lower()
                or "size" in ctx_bomb.exception.detail.lower()
                or "threshold" in ctx_bomb.exception.detail.lower(),
                f"Detail must indicate zip bomb size error: {ctx_bomb.exception.detail}",
            )

            # 3. Kasus C: Arsip ZIP Valid dan Aman
            zip_buffer_safe = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_safe, "w") as zf:
                zf.writestr("corpus_doc1.txt", "Konten naskah skripsi pembanding satu.")
                zf.writestr("subfolder/corpus_doc2.txt", "Konten naskah skripsi pembanding dua.")
            zip_buffer_safe.seek(0)

            extracted_files = CorpusService.extract_zip_safely(
                zip_file=zip_buffer_safe,
                target_dir=extract_dir,
                max_uncompressed_bytes=200 * 1024 * 1024,
            )
            self.assertEqual(len(extracted_files), 2)
            for fpath in extracted_files:
                self.assertTrue(os.path.exists(fpath))
                self.assertTrue(os.path.abspath(fpath).startswith(os.path.abspath(extract_dir)))

            # 4. Kasus D: Serangan Symlink (Archive member with symlink header)
            zip_buffer_symlink = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_symlink, "w") as zf:
                zinfo = zipfile.ZipInfo("symlink_target")
                zinfo.create_system = 3  # Unix
                zinfo.external_attr = 0o120777 << 16  # S_IFLNK
                zf.writestr(zinfo, "/etc/passwd")
            zip_buffer_symlink.seek(0)

            with self.assertRaises(HTTPException) as ctx_symlink:
                CorpusService.extract_zip_safely(
                    zip_file=zip_buffer_symlink,
                    target_dir=extract_dir,
                )
            self.assertEqual(ctx_symlink.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("symbolic link", ctx_symlink.exception.detail.lower())

            # 5. Kasus E: Berkas korup bukan format ZIP valid
            corrupt_buffer = io.BytesIO(b"bukan_format_zip_valid_binary_random_garbage")
            with self.assertRaises(HTTPException) as ctx_corrupt:
                CorpusService.extract_zip_safely(
                    zip_file=corrupt_buffer,
                    target_dir=extract_dir,
                )
            self.assertEqual(ctx_corrupt.exception.status_code, status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    unittest.main()
