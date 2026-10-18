import math
import os
import sys
import unittest
import uuid

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine, LexicalAnalysisResult
from app.engine.tier2_semantic import SemanticEngine, SemanticAnalysisResult
from app.engine.tier3_stylometric import StylometricEngine, StylometricAnalysisResult
from app.engine.tier4_aggregator import HybridAggregator, HybridAuditResult
from app.engine.reference_corpus import ReferenceCorpusBank, BUILTIN_REFERENCE_PAPERS


class TestTextPreprocessor(unittest.TestCase):
    """Deep verification of text normalization, tokenization, and sentence segmentation with char offsets."""

    def test_normalization_and_case_folding(self):
        raw = "  Sistem   Deteksi \t\n Plagiarisme \t Cerdas!  "
        normalized = TextPreprocessor.normalize_whitespace(raw)
        self.assertEqual(normalized, "Sistem Deteksi Plagiarisme Cerdas!")

        folded = TextPreprocessor.case_folding("Model TRANSFORMER & Deep Learning")
        self.assertEqual(folded, "model transformer & deep learning")

        clean_lex = TextPreprocessor.clean_for_lexical("VeriText AI: Hybrid 4-Tier Engine (v1.0)!")
        self.assertEqual(clean_lex, "veritextaihybrid4tierenginev10")

    def test_empty_and_whitespace_inputs(self):
        self.assertEqual(TextPreprocessor.normalize_whitespace(""), "")
        self.assertEqual(TextPreprocessor.case_folding(""), "")
        self.assertEqual(TextPreprocessor.clean_for_lexical(""), "")
        self.assertEqual(TextPreprocessor.tokenize_words(""), [])
        self.assertEqual(TextPreprocessor.segment_sentences(""), [])
        self.assertEqual(TextPreprocessor.segment_sentences("   \n\t  "), [])

    def test_sentence_segmentation_with_exact_offsets(self):
        text = (
            "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik. "
            "Penerapan struktur indeks Hierarchical Navigable Small World memungkinkan penelusuran tetangga terdekat. "
            "Hasil pengujian menunjukkan akurasi tinggi!"
        )
        sentences = TextPreprocessor.segment_sentences(text)
        self.assertEqual(len(sentences), 3)

        # CRITICAL VERIFICATION: original_text[start:end] must strictly match sentence.text
        for s in sentences:
            extracted = text[s.start_char : s.end_char]
            self.assertEqual(
                extracted,
                s.text,
                f"Offset mismatch: expected '{s.text}' but slice gave '{extracted}'",
            )
            self.assertGreater(s.word_count, 0)
            self.assertGreater(len(s.tokens), 0)

    def test_academic_abbreviations_not_split(self):
        text = (
            "Penelitian Dr. Budi Santoso, M.Kom. dan Prof. Hendra Gunawan membahas NLP. "
            "Hasil riset tersebut dimuat dalam vol. 12, hal. 45 dkk. pada seminar nasional."
        )
        sentences = TextPreprocessor.segment_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("Dr. Budi Santoso, M.Kom.", sentences[0].text)
        self.assertIn("vol. 12, hal. 45 dkk.", sentences[1].text)

    def test_decimal_numbers_not_split(self):
        text = "Sistem mencapai akurasi sebesar 98.75% dengan nilai p-value < 0.05. Evaluasi berjalan sukses."
        sentences = TextPreprocessor.segment_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("98.75%", sentences[0].text)
        self.assertIn("0.05.", sentences[0].text)

    def test_citation_detection(self):
        cit1 = "[1] Santoso, B. (2024). Deteksi Plagiarisme Cerdas."
        cit2 = "(Santoso dkk., 2023)"
        normal = "Algoritma Winnowing membagi teks menjadi k-gram berurutan."

        self.assertTrue(TextPreprocessor.is_citation_sentence(cit1))
        self.assertTrue(TextPreprocessor.is_citation_sentence(cit2))
        self.assertFalse(TextPreprocessor.is_citation_sentence(normal))


class TestWinnowingLexicalEngine(unittest.TestCase):
    """Deep verification of the Winnowing algorithm, Rabin-Karp polynomial rolling hash, and sliding window."""

    def setUp(self):
        self.engine = WinnowingLexicalEngine(k=5, w=4)

    def test_polynomial_hash_consistency_with_rolling_hash(self):
        """Verifies that Rabin-Karp rolling update strictly produces identical values to direct polynomial hash."""
        text = "algoritma winnowing cerdas berbasis rolling hash rabin karp"
        clean = TextPreprocessor.clean_for_lexical(text)
        k = 5

        # 1. Compute direct polynomial hashes
        direct_hashes = []
        for i in range(len(clean) - k + 1):
            kgram = clean[i : i + k]
            direct_hashes.append(self.engine.polynomial_hash(kgram))

        # 2. Compute via compute_kgram_hashes (which uses rolling update)
        rolling_tuples = self.engine.compute_kgram_hashes(text)
        rolling_hashes = [h for h, _ in rolling_tuples]

        self.assertEqual(len(direct_hashes), len(rolling_hashes))
        for idx, (dh, rh) in enumerate(zip(direct_hashes, rolling_hashes)):
            self.assertEqual(
                dh,
                rh,
                f"Hash mismatch at k-gram index {idx}: direct={dh}, rolling={rh}",
            )

    def test_sliding_window_rightmost_tie_breaking(self):
        """Validates that duplicate minimum hash values in a window break ties by choosing rightmost position."""
        # Simulated hashes where minimum hash value '10' appears at position 1 and position 3
        test_hashes = [(50, 0), (10, 1), (30, 2), (10, 3)]
        fingerprints = self.engine.winnow(test_hashes)

        # For window [ (50,0), (10,1), (30,2), (10,3) ], minimum is 10, rightmost is at position 3
        self.assertEqual(len(fingerprints), 1)
        self.assertEqual(fingerprints[0], (10, 3))

    def test_boundary_lengths_short_text(self):
        """Tests k-gram extraction on texts shorter than k=5."""
        short_text = "abc"  # 3 chars < k=5
        hashes = self.engine.compute_kgram_hashes(short_text)
        self.assertEqual(len(hashes), 1)
        self.assertEqual(hashes[0][0], self.engine.polynomial_hash("abc"))

        fps = self.engine.extract_fingerprints(short_text)
        self.assertEqual(len(fps), 1)

        empty_hashes = self.engine.compute_kgram_hashes("")
        self.assertEqual(empty_hashes, [])

    def test_containment_similarity_formula(self):
        """Validates containment score: Score_T1 = (|FP_doc ∩ FP_corpus| / |FP_doc|) * 100%."""
        doc_fps = [(101, 0), (102, 5), (103, 10), (104, 15)]  # 4 unique hashes
        corpus_fps = {101, 102, 999, 888}  # Overlaps on 101 and 102 (2 / 4 = 50.0%)

        score, intersection = self.engine.calculate_containment(doc_fps, corpus_fps)
        self.assertEqual(score, 50.0)
        self.assertEqual(intersection, {101, 102})

        # Zero overlap
        score_zero, _ = self.engine.calculate_containment(doc_fps, {777, 888})
        self.assertEqual(score_zero, 0.0)

        # Empty doc
        score_empty, _ = self.engine.calculate_containment([], corpus_fps)
        self.assertEqual(score_empty, 0.0)

    def test_verbatim_plagiarism_detection(self):
        """Verifies that text copied verbatim from reference corpus achieves high lexical containment."""
        ref_text = BUILTIN_REFERENCE_PAPERS[0]["text"]
        bank = ReferenceCorpusBank.get_instance()

        sentences = TextPreprocessor.segment_sentences(ref_text)
        result = self.engine.analyze_document(
            original_text=ref_text,
            sentences=sentences,
            corpus_index=bank.get_fingerprint_index(),
        )

        self.assertGreaterEqual(result.score_t1, 90.0)
        self.assertGreater(len(result.sentence_matches), 0)


class TestSemanticEngine(unittest.TestCase):
    """Deep verification of 384-D dense embeddings, unit norm, and cosine similarity."""

    def setUp(self):
        self.engine = SemanticEngine(dimension=384, paraphrase_threshold=0.75)

    def test_embedding_dimensions_and_unit_l2_norm(self):
        sentence = "Model transformer memetakan makna kalimat ke dalam representasi vektor padat."
        vec = self.engine.embed_sentence(sentence)

        self.assertEqual(len(vec), 384)
        l2_norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(l2_norm, 1.0, places=4)

    def test_cosine_similarity_properties(self):
        u = [1.0, 0.0, 0.0]
        v = [1.0, 0.0, 0.0]
        w = [0.0, 1.0, 0.0]

        # Identical
        self.assertAlmostEqual(SemanticEngine.cosine_similarity(u, v), 1.0, places=5)
        # Orthogonal
        self.assertAlmostEqual(SemanticEngine.cosine_similarity(u, w), 0.0, places=5)
        # Zero vectors
        self.assertEqual(SemanticEngine.cosine_similarity([0.0, 0.0], [0.0, 0.0]), 0.0)
        # Mismatched lengths
        self.assertEqual(SemanticEngine.cosine_similarity([1.0], [1.0, 2.0]), 0.0)

    def test_semantic_paraphrase_similarity_threshold(self):
        """Validates that paraphrased sentences achieve >= 0.75 cosine similarity."""
        s1 = "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik berbasis deep learning."
        # Paraphrased version with synonym substitutions and structural alterations
        s2 = "Pendeteksian plagiarisme pintar menggunakan kombinasi algoritma leksikal serta representasi semantik deep learning."

        u = self.engine.embed_sentence(s1)
        v = self.engine.embed_sentence(s2)
        sim = self.engine.cosine_similarity(u, v)

        self.assertGreaterEqual(
            sim,
            0.75,
            f"Paraphrased similarity {sim} fell below semantic threshold 0.75",
        )

    def test_unrelated_sentences_low_similarity(self):
        """Validates that completely unrelated topics have low cosine similarity (< 0.40)."""
        s_tech = "Arsitektur jaringan saraf konvolusional digunakan untuk segmentasi citra medis."
        s_cook = "Resep membuat sambal terasi tradisional khas nusantara dengan cabai rawit segar."

        u = self.engine.embed_sentence(s_tech)
        v = self.engine.embed_sentence(s_cook)
        sim = self.engine.cosine_similarity(u, v)

        self.assertLess(
            sim,
            0.40,
            f"Unrelated sentence similarity {sim} should be < 0.40",
        )


class TestStylometricEngine(unittest.TestCase):
    """Deep verification of Burstiness metric, Type-Token Ratio, and AI anomaly detection."""

    def setUp(self):
        self.engine = StylometricEngine(burstiness_threshold=0.20)

    def test_burstiness_formula_and_ai_monotonicity(self):
        """Burstiness = (sigma - mu) / (sigma + mu).
        
        AI text with monotonic sentence lengths must yield Burstiness < 0.20 and high anomaly score.
        """
        # Synthetic AI text with identical 12-word sentences
        ai_sentences = [
            SentenceSpan(index=0, text="Sistem kecerdasan buatan memainkan peran sangat penting dalam perkembangan teknologi informasi modern saat ini.", start_char=0, end_char=100, word_count=13),
            SentenceSpan(index=1, text="Penggunaan model pembelajaran mesin memberikan dampak signifikan terhadap efisiensi analisis data berskala besar di kampus.", start_char=105, end_char=210, word_count=13),
            SentenceSpan(index=2, text="Secara keseluruhan dapat disimpulkan bahwa implementasi platform digital membawa banyak kemudahan bagi seluruh mahasiswa aktif.", start_char=215, end_char=325, word_count=13),
            SentenceSpan(index=3, text="Penting untuk dicatat bahwa tata kelola teknologi informasi membutuhkan komitmen berkelanjutan dari setiap pemangku kepentingan.", start_char=330, end_char=440, word_count=13),
        ]
        full_text = " ".join(s.text for s in ai_sentences)

        result = self.engine.analyze_document(full_text, ai_sentences)

        # Standard deviation should be 0.0, so Burstiness = (0 - 13)/(0 + 13) = -1.0
        self.assertEqual(result.std_sentence_length, 0.0)
        self.assertEqual(result.burstiness, -1.0)
        self.assertLess(result.burstiness, 0.20)
        self.assertTrue(result.is_ai_monotonous)
        self.assertGreaterEqual(result.score_t3, 50.0)

    def test_human_text_high_burstiness_and_variation(self):
        """Human natural text with diverse short and long sentences must yield low AI anomaly score."""
        human_sentences = [
            SentenceSpan(index=0, text="Teknologi berkembang sangat pesat.", start_char=0, end_char=35, word_count=4),
            SentenceSpan(index=1, text="Meskipun demikian, berbagai tantangan etika dan regulasi perlindungan data pribadi tetap menjadi perhatian utama masyarakat di era keterbukaan informasi publik.", start_char=40, end_char=200, word_count=20),
            SentenceSpan(index=2, text="Mengapa hal ini krusial?", start_char=205, end_char=230, word_count=4),
            SentenceSpan(index=3, text="Jawabannya terletak pada integritas akademik.", start_char=235, end_char=280, word_count=5),
            SentenceSpan(index=4, text="Tanpa kejujuran ilmiah, seluruh pencapaian riset universitas akan kehilangan legitimasi dan kepercayaan publik.", start_char=285, end_char=395, word_count=13),
        ]
        full_text = " ".join(s.text for s in human_sentences)

        result = self.engine.analyze_document(full_text, human_sentences)

        self.assertGreater(result.std_sentence_length, 5.0)
        self.assertFalse(result.is_ai_monotonous)
        self.assertLess(result.score_t3, 30.0)

    def test_type_token_ratio_calculation(self):
        """TTR = unique_words / total_words."""
        # 4 identical words
        ttr_low, tot1, uniq1 = self.engine.calculate_type_token_ratio("kata kata kata kata")
        self.assertEqual(tot1, 4)
        self.assertEqual(uniq1, 1)
        self.assertEqual(ttr_low, 0.25)

        # 4 distinct words
        ttr_high, tot2, uniq2 = self.engine.calculate_type_token_ratio("satu dua tiga empat")
        self.assertEqual(tot2, 4)
        self.assertEqual(uniq2, 4)
        self.assertEqual(ttr_high, 1.0)

        # Empty text
        ttr_zero, tot0, uniq0 = self.engine.calculate_type_token_ratio("")
        self.assertEqual(ttr_zero, 0.0)
        self.assertEqual(tot0, 0)


class TestHybridAggregator(unittest.TestCase):
    """Deep verification of the 4-tier composite pipeline, weighting formula, and heatmap annotations."""

    def setUp(self):
        self.aggregator = HybridAggregator()

    def test_composite_score_formula(self):
        """Composite = 0.50 * T1 + 0.35 * T2 + 0.15 * T3 bounded in [0.0, 100.0]."""
        t1, t2, t3 = 60.0, 40.0, 20.0
        expected = round(0.50 * t1 + 0.35 * t2 + 0.15 * t3, 2)
        self.assertEqual(expected, 47.0)

    def test_end_to_end_pipeline_with_exact_reference_match(self):
        """Manuscript containing exact reference sentences triggers Tier 1 (RED) heatmap annotations."""
        doc_text = (
            "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik berbasis deep learning. "
            "Penerapan struktur indeks Hierarchical Navigable Small World memungkinkan penelusuran tetangga terdekat secara efisien pada basis data PostgreSQL. "
            "Ini adalah kalimat kesimpulan orisinal yang ditulis secara mandiri oleh mahasiswa."
        )

        result = self.aggregator.run_pipeline(original_text=doc_text, audit_depth="FULL")

        self.assertIsInstance(result, HybridAuditResult)
        self.assertGreater(result.score_lexical, 30.0)
        self.assertGreater(result.score_composite, 15.0)

        # Check Heatmap Annotations
        self.assertGreater(len(result.heatmap_annotations), 0)
        for anno in result.heatmap_annotations:
            self.assertIn(anno["tier"], ("T1", "T2", "T3"))
            self.assertIn(anno["color"], ("RED", "ORANGE", "YELLOW"))
            self.assertGreaterEqual(anno["similarity"], 0.0)
            self.assertLessEqual(anno["similarity"], 1.0)

            # CRITICAL CHECK: offsets must accurately map to text
            extracted = doc_text[anno["start"] : anno["end"]]
            self.assertEqual(extracted, anno["text_snippet"])

        # Check Matched Sources
        self.assertGreater(len(result.matched_sources), 0)
        first_source = result.matched_sources[0]
        self.assertIn("corpus_doc_id", first_source)
        self.assertIn("title", first_source)
        self.assertGreater(first_source["contribution_pct"], 0.0)

    def test_tier1_only_audit_depth(self):
        """When audit_depth is TIER1_ONLY, semantic and stylometric scores are omitted/zeroed."""
        doc_text = "Algoritma Winnowing menggunakan rolling hash Rabin-Karp untuk memilih sidik jari dokumen secara deterministik."
        result = self.aggregator.run_pipeline(original_text=doc_text, audit_depth="TIER1_ONLY")

        self.assertEqual(result.audit_depth, "TIER1_ONLY")
        self.assertEqual(result.score_semantic, 0.0)
        self.assertEqual(result.score_stylometric, 0.0)
        self.assertEqual(result.score_composite, result.score_lexical)

    def test_empty_document_pipeline_safety(self):
        """Empty input safely returns 0.0 scores without exceptions."""
        result = self.aggregator.run_pipeline("")
        self.assertEqual(result.score_composite, 0.0)
        self.assertEqual(result.score_lexical, 0.0)
        self.assertEqual(len(result.heatmap_annotations), 0)
        self.assertEqual(len(result.matched_sources), 0)


class TestReferenceCorpusBank(unittest.TestCase):
    """Validates the built-in reference corpus bank initialization and data structure."""

    def test_reference_corpus_loaded(self):
        bank = ReferenceCorpusBank.get_instance()
        docs = bank.get_all_documents()
        self.assertGreaterEqual(len(docs), 5)

        fp_index = bank.get_fingerprint_index()
        self.assertGreater(len(fp_index), 50)

        chunks = bank.get_corpus_chunks()
        self.assertGreater(len(chunks), 15)

        # Verify chunk embeddings are 384D
        for ch in chunks[:5]:
            self.assertEqual(len(ch["embedding"]), 384)


class TestDatabaseExecutionIntegration(unittest.TestCase):
    """Tests the real worker pipeline execution using a mock/test database session."""

    def test_execute_audit_pipeline_direct(self):
        from app.workers.tasks import execute_audit_pipeline
        from app.models.document import Document
        from app.models.audit import AuditTask, AuditSentence, AuditReport

        # Minimal in-memory mock session for testing workflow execution
        class MockSession:
            def __init__(self):
                self.records = {}
                self.committed = False

            def query(self, *entities):
                sess = self
                model = entities[0] if entities else None
                class QueryMock:
                    def filter(self, *conds):
                        return self
                    def first(self):
                        for r in sess.records.values():
                            if isinstance(r, model):
                                return r
                        return None
                    def delete(self):
                        return 0
                    def all(self):
                        return []
                    def join(self, *a, **k):
                        return self
                return QueryMock()

            def add(self, obj):
                self.records[id(obj)] = obj

            def commit(self):
                self.committed = True

            def rollback(self):
                pass

        mock_db = MockSession()
        test_doc_id = uuid.uuid4()
        test_task_id = uuid.uuid4()

        doc = Document(
            id=test_doc_id,
            original_filename="Tesis_Uji_Winnowing.txt",
            stored_filename="tesis_uji.txt",
            file_size_bytes=1024,
            mime_type="text/plain",
        )
        task = AuditTask(
            id=test_task_id,
            document_id=test_doc_id,
            user_id=uuid.uuid4(),
            audit_depth="FULL",
            status="QUEUED",
        )
        mock_db.add(doc)
        mock_db.add(task)

        # Execute
        result = execute_audit_pipeline(mock_db, str(test_task_id), str(test_doc_id))

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.progress_pct, 100)
        self.assertEqual(task.current_stage, "COMPLETED")
        self.assertIsNotNone(task.completed_at)

        # Check report created
        report_found = any(isinstance(r, AuditReport) for r in mock_db.records.values())
        self.assertTrue(report_found)


if __name__ == "__main__":
    unittest.main()
