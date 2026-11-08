import uuid
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.engine.preprocessor import TextPreprocessor

BASE_REFERENCE_PAPERS: list[dict[str, Any]] = [
    {
        "id": "c1111111-1111-1111-1111-111111111111",
        "title": "Analisis Performa Model Transformer pada Pemrosesan Teks Bahasa Indonesia",
        "category": "Informatika / AI",
        "academic_year": "2024/2025",
        "text": (
            "Deteksi plagiarisme cerdas memanfaatkan perpaduan algoritma leksikal dan representasi "
            "semantik berbasis deep learning. Penerapan struktur indeks Hierarchical Navigable "
            "Small World memungkinkan penelusuran tetangga terdekat secara efisien pada basis data "
            "PostgreSQL. Model pra-latih Transformer seperti IndoBERT dan MiniLM terbukti unggul "
            "dalam mengenali makna kontekstual kalimat. Eksperimen menunjukkan bahwa representasi "
            "vektor 384 dimensi mampu mengidentifikasi parafrasa teks dengan presisi "
            "tinggi. Penggunaan ruang embedding terstandarisasi mengatasi keterbatasan pencocokan "
            "kata demi kata yang rentan terhadap substitusi sinonim."
        ),
    },
    {
        "id": "c2222222-2222-2222-2222-222222222222",
        "title": "Implementasi Sistem Deteksi Plagiarisme Cerdas Menggunakan Arsitektur Hybrid",
        "category": "Rekayasa Perangkat Lunak",
        "academic_year": "2024/2025",
        "text": (
            "Implementasi sistem deteksi plagiarisme cerdas memerlukan integrasi antara pemrosesan "
            "bahasa alami deterministik dan komputasi vektor. Pendekatan berbasis representasi "
            "vektor padat kalimat membuktikan efektivitas tinggi dalam mengenali parafrasa "
            "terstruktur. Arsitektur pipa multi-tier menggabungkan efisiensi penapisan leksikal "
            "dengan ketepatan analisis semantik tingkat lanjut. Sistem menghasilkan anotasi "
            "heatmap berwarna untuk membedakan plagiarisme verbatim, parafrasa, dan anomali "
            "sintaksis. Penerapan bobot agregasi komposit menjamin keadilan evaluasi karya tulis "
            "secara objektif."
        ),
    },
    {
        "id": "c3333333-3333-3333-3333-333333333333",
        "title": "Penerapan Algoritma Winnowing dan Rolling Hash untuk Temu Kembali Informasi",
        "category": "Ilmu Komputer",
        "academic_year": "2023/2024",
        "text": (
            "Algoritma Winnowing menggunakan rolling hash Rabin-Karp untuk memilih sidik jari "
            "dokumen secara deterministik. Dengan sliding window berukuran w, nilai hash minimum "
            "pada setiap jendela dipilih sebagai representasi naskah. Aturan pemecahan seri "
            "memilih posisi paling kanan guna mencegah redudansi sidik jari yang berdekatan. "
            "Pengukuran nilai containment membandingkan irisan sidik jari naskah uji terhadap bank "
            "korpus pembanding. Metode ini terbukti memiliki kompleksitas waktu linier dan tahan "
            "terhadap manipulasi urutan kalimat kecil."
        ),
    },
]


def sync_corpus_records(
    documents: list[dict[str, Any]], lex_engine: Any, sem_engine: Any, db_session: Any
) -> int:
    """Synchronizes reference corpus documents to the PostgreSQL database."""
    try:
        from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
        from app.models.user import User

        admin = db_session.query(User).filter(User.role == "ADMIN").first()
        admin_id = admin.id if admin else uuid.UUID("11111111-1111-1111-1111-111111111111")
        synced = 0
        for doc in documents:
            doc_uuid = uuid.UUID(doc["id"])
            if db_session.query(CorpusDocument).filter(CorpusDocument.id == doc_uuid).first():
                continue
            rec = CorpusDocument(
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
            db_session.add(rec)
            db_session.flush()
            sentences = TextPreprocessor.segment_sentences(doc["text"])
            for idx, s in enumerate(sentences):
                db_session.add(DocumentChunk(
                    corpus_doc_id=doc_uuid,
                    chunk_index=idx,
                    chunk_text=s.text,
                    embedding=sem_engine.embed_sentence(s.text),
                    start_char=s.start_char,
                    end_char=s.end_char,
                ))
            for h_val, pos in lex_engine.extract_fingerprints(doc["text"]):
                db_session.add(LexicalFingerprint(
                    corpus_doc_id=doc_uuid,
                    fingerprint_hash=h_val,
                    position_start=pos,
                    position_end=pos + lex_engine.k,
                ))
            rec.total_chunks = len(sentences)
            synced += 1
        if synced > 0:
            db_session.commit()
        return synced
    except (SQLAlchemyError, Exception):  # noqa: BLE001
        db_session.rollback()
        return 0
