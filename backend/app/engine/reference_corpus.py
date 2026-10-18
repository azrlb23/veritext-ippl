import uuid
from typing import Any, Dict, List, Optional

from app.engine.preprocessor import TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine


BUILTIN_REFERENCE_PAPERS = [
    {
        "id": "c1111111-1111-1111-1111-111111111111",
        "title": "Analisis Performa Model Transformer pada Pemrosesan Teks Bahasa Indonesia",
        "category": "Informatika / AI",
        "academic_year": "2024/2025",
        "text": (
            "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi semantik berbasis deep learning. "
            "Penerapan struktur indeks Hierarchical Navigable Small World memungkinkan penelusuran tetangga terdekat secara efisien pada basis data PostgreSQL. "
            "Model pra-latih Transformer seperti IndoBERT dan MiniLM terbukti unggul dalam mengenali makna kontekstual kalimat. "
            "Eksperimen menunjukkan bahwa representasi vektor 384 dimensi mampu mengidentifikasi parafrasa teks akademik dengan presisi tinggi. "
            "Penggunaan ruang embedding terstandarisasi mengatasi keterbatasan pencocokan kata demi kata yang rentan terhadap substitusi sinonim."
        ),
    },
    {
        "id": "c2222222-2222-2222-2222-222222222222",
        "title": "Implementasi Sistem Deteksi Plagiarisme Cerdas Menggunakan Arsitektur Hybrid",
        "category": "Rekayasa Perangkat Lunak",
        "academic_year": "2024/2025",
        "text": (
            "Implementasi sistem deteksi plagiarisme cerdas memerlukan integrasi antara pemrosesan bahasa alami deterministik dan komputasi vektor. "
            "Pendekatan berbasis representasi vektor padat kalimat membuktikan efektivitas tinggi dalam mengenali parafrasa terstruktur. "
            "Arsitektur pipa multi-tier menggabungkan efisiensi penapisan leksikal dengan ketepatan analisis semantik tingkat lanjut. "
            "Sistem menghasilkan anotasi heatmap berwarna untuk membedakan plagiarisme verbatim, parafrasa, dan anomali sintaksis. "
            "Penerapan bobot agregasi komposit menjamin keadilan evaluasi karya ilmiah mahasiswa secara objektif."
        ),
    },
    {
        "id": "c3333333-3333-3333-3333-333333333333",
        "title": "Penerapan Algoritma Winnowing dan Rolling Hash untuk Temu Kembali Informasi",
        "category": "Ilmu Komputer",
        "academic_year": "2023/2024",
        "text": (
            "Algoritma Winnowing menggunakan rolling hash Rabin-Karp untuk memilih sidik jari dokumen secara deterministik. "
            "Dengan sliding window berukuran w, nilai hash minimum pada setiap jendela dipilih sebagai representasi naskah. "
            "Aturan pemecahan seri memilih posisi paling kanan guna mencegah redudansi sidik jari yang berdekatan. "
            "Pengukuran nilai containment membandingkan irisan sidik jari naskah uji terhadap bank korpus pembanding. "
            "Metode ini terbukti memiliki kompleksitas waktu linier dan tahan terhadap manipulasi urutan kalimat kecil."
        ),
    },
    {
        "id": "c4444444-4444-4444-4444-444444444444",
        "title": "Optimasi Pencarian Vektor Menggunakan Indeks HNSW pada Basis Data Terdistribusi",
        "category": "Sistem Informasi",
        "academic_year": "2025/2026",
        "text": (
            "Pencarian kemiripan kosinus berdimensi tinggi membutuhkan mekanisme indeks aproksimasi graf yang efisien. "
            "Indeks Hierarchical Navigable Small World membagi titik data ke dalam beberapa lapisan graf dengan kerapatan bervariasi. "
            "Eksplorasi graf dimulai dari lapisan teratas yang renggang menuju lapisan dasar dengan recall mendekati optimal. "
            "Integrasi ekstensi pgvector pada PostgreSQL menyediakan kapasitas skalabilitas tinggi tanpa dependensi mesin pencari eksternal. "
            "Konfigurasi parameter m dan ef_construction sangat memengaruhi keseimbangan antara kecepatan komputasi dan akurasi temu kembali."
        ),
    },
    {
        "id": "c5555555-5555-5555-5555-555555555555",
        "title": "Etika Akademik dan Deteksi Tulisan Berbantuan Kecerdasan Buatan Generatif",
        "category": "Pendidikan & Etika",
        "academic_year": "2025/2026",
        "text": (
            "Karakteristik teks buatan model bahasa besar cenderung memiliki keragaman leksikal yang seragam serta variasi panjang kalimat yang monoton. "
            "Analisis stilometri memanfaatkan metrik burstiness untuk mendeteksi varians ritme kalimat yang tidak wajar pada naskah akademik. "
            "Nilai Type-Token Ratio mencerminkan kekayaan kosakata yang sering kali terdistribusi secara kaku pada teks sintetis AI. "
            "Pencegahan pelanggaran integritas akademik membutuhkan pemahaman komprehensif atas batasan penggunaan kecerdasan buatan dalam penulisan ilmiah. "
            "Institusi pendidikan tinggi wajib merumuskan pedoman transparan untuk memverifikasi keaslian karya mahasiswa."
        ),
    },
]


class ReferenceCorpusBank:
    """Built-in Reference Corpus Bank providing in-memory indexed reference documents.
    
    Allows immediate, zero-configuration plagiarism testing against established reference papers
    even when running offline or without an active database connection.
    """

    _instance: Optional["ReferenceCorpusBank"] = None

    def __init__(self):
        self.documents = BUILTIN_REFERENCE_PAPERS
        self.lexical_engine = WinnowingLexicalEngine()
        self.semantic_engine = SemanticEngine()

        # Indexes
        self.fingerprint_index: Dict[int, List[Dict[str, Any]]] = {}
        self.corpus_chunks: List[Dict[str, Any]] = []

        self._build_indexes()

    @classmethod
    def get_instance(cls) -> "ReferenceCorpusBank":
        if cls._instance is None:
            cls._instance = ReferenceCorpusBank()
        return cls._instance

    def _build_indexes(self):
        """Indexes all reference documents into lexical fingerprints and semantic chunks."""
        self.fingerprint_index.clear()
        self.corpus_chunks.clear()

        for doc in self.documents:
            doc_id = doc["id"]
            title = doc["title"]
            category = doc["category"]
            text = doc["text"]

            # 1. Segment sentences
            sentences = TextPreprocessor.segment_sentences(text)

            # 2. Build Lexical Fingerprints
            fps = self.lexical_engine.extract_fingerprints(text)
            for h_val, pos in fps:
                if h_val not in self.fingerprint_index:
                    self.fingerprint_index[h_val] = []
                self.fingerprint_index[h_val].append({
                    "doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "position": pos,
                })

            # 3. Build Semantic Chunks (per-sentence chunks for dense vector comparison)
            for s in sentences:
                chunk_id = str(uuid.uuid4())
                embedding = self.semantic_engine.embed_sentence(s.text)
                self.corpus_chunks.append({
                    "chunk_id": chunk_id,
                    "corpus_doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "chunk_text": s.text,
                    "embedding": embedding,
                    "start_char": s.start_char,
                    "end_char": s.end_char,
                })

    def get_fingerprint_index(self) -> Dict[int, List[Dict[str, Any]]]:
        return self.fingerprint_index

    def get_corpus_chunks(self) -> List[Dict[str, Any]]:
        return self.corpus_chunks

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.documents

    def sync_to_db(self, db_session) -> int:
        """Syncs built-in reference corpus into PostgreSQL database if not already present."""
        try:
            from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
            from app.models.user import User

            # Find an admin or system user
            admin_user = db_session.query(User).filter(User.role == "ADMIN").first()
            admin_id = admin_user.id if admin_user else uuid.UUID("11111111-1111-1111-1111-111111111111")

            synced_count = 0
            for doc in self.documents:
                doc_uuid = uuid.UUID(doc["id"])
                existing = db_session.query(CorpusDocument).filter(CorpusDocument.id == doc_uuid).first()
                if existing:
                    continue

                corpus_record = CorpusDocument(
                    id=doc_uuid,
                    uploaded_by=admin_id,
                    title=doc["title"],
                    category=doc["category"],
                    academic_year=doc["academic_year"],
                    stored_filename=f"ref_{doc_uuid.hex[:12]}.txt",
                    sha256_hash=uuid.uuid5(uuid.NAMESPACE_DNS, doc["title"]).hex,
                    status="INDEXED",
                    total_chunks=0,
                )
                db_session.add(corpus_record)
                db_session.flush()

                # Add chunks
                sentences = TextPreprocessor.segment_sentences(doc["text"])
                for idx, s in enumerate(sentences):
                    emb = self.semantic_engine.embed_sentence(s.text)
                    chunk_rec = DocumentChunk(
                        corpus_doc_id=doc_uuid,
                        chunk_index=idx,
                        chunk_text=s.text,
                        embedding=emb,
                        start_char=s.start_char,
                        end_char=s.end_char,
                    )
                    db_session.add(chunk_rec)

                # Add fingerprints
                fps = self.lexical_engine.extract_fingerprints(doc["text"])
                for h_val, pos in fps:
                    fp_rec = LexicalFingerprint(
                        corpus_doc_id=doc_uuid,
                        fingerprint_hash=h_val,
                        position_start=pos,
                        position_end=pos + self.lexical_engine.k,
                    )
                    db_session.add(fp_rec)

                corpus_record.total_chunks = len(sentences)
                synced_count += 1

            if synced_count > 0:
                db_session.commit()
            return synced_count
        except Exception:
            db_session.rollback()
            return 0
