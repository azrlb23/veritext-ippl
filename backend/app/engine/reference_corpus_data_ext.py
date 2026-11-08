from typing import Any

EXT_REFERENCE_PAPERS: list[dict[str, Any]] = [
    {
        "id": "c4444444-4444-4444-4444-444444444444",
        "title": "Optimasi Pencarian Vektor Menggunakan Indeks HNSW pada Basis Data Terdistribusi",
        "category": "Sistem Informasi",
        "academic_year": "2025/2026",
        "text": (
            "Pencarian kemiripan kosinus berdimensi tinggi membutuhkan mekanisme indeks aproksimasi "
            "graf yang efisien. Indeks Hierarchical Navigable Small World membagi titik data ke "
            "dalam beberapa lapisan graf dengan kerapatan bervariasi. Eksplorasi graf dimulai dari "
            "lapisan teratas yang renggang menuju lapisan dasar dengan recall mendekati optimal. "
            "Integrasi ekstensi pgvector pada PostgreSQL menyediakan kapasitas skalabilitas tinggi "
            "tanpa dependensi mesin pencari eksternal. Konfigurasi parameter m dan ef_construction "
            "sangat memengaruhi keseimbangan antara kecepatan komputasi dan akurasi temu kembali."
        ),
    },
    {
        "id": "c5555555-5555-5555-5555-555555555555",
        "title": "Etika dan Deteksi Tulisan Berbantuan Kecerdasan Buatan Generatif",
        "category": "Pendidikan & Etika",
        "academic_year": "2025/2026",
        "text": (
            "Karakteristik teks buatan model bahasa besar cenderung memiliki keragaman leksikal "
            "yang seragam serta variasi panjang kalimat yang monoton. Analisis stilometri "
            "memanfaatkan metrik burstiness untuk mendeteksi varians ritme kalimat yang tidak "
            "wajar pada naskah tulis. Nilai Type-Token Ratio mencerminkan kekayaan kosakata yang "
            "sering kali terdistribusi secara kaku pada teks sintetis AI. Pencegahan pelanggaran "
            "orisinalitas teks membutuhkan pemahaman komprehensif atas batasan penggunaan "
            "kecerdasan buatan dalam penulisan. Setiap penerbit wajib merumuskan "
            "pedoman transparan untuk memverifikasi keaslian karya."
        ),
    },
]
