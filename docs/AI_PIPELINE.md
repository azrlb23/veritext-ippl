# AI Pipeline & Detection Engine: VeriText AI

Dokumen ini mendefinisikan arsitektur pipa komputasi kecerdasan buatan 3-tahap (*3-Step Hybrid AI Pipeline*), formula pembobotan skor komposit, akuisisi korpus otomatis dwilingkup (*Dual-Scope*), serta mekanisme *Dual-Engine LLM Gateway* berfitur toleransi kegagalan otomatis (*automatic failover*).

---

## 1. Tinjauan Pipa Deteksi Hybrid 3-Tahap

Deteksi plagiarisme VeriText AI dirancang untuk memecahkan kelemahan metode leksikal konvensional (yang mudah tertipu parafrase cerdas) maupun metode LLM murni (yang lambat, boros kuota token, dan rentan positif palsu pada sitasi sah).

```
                                  [ Teks Naskah Masukan ]
                                             │
                        ┌────────────────────┴────────────────────┐
                        ▼                                         ▼
            [ Ekstraksi Teks Bersih ]                  [ Segmentasi Kalimat ]
                        │                                         │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
         ┌────────────────────────────────────────────────────────────────────────┐
         │ STEP 1: DETEKSI LEKSIKAL WINNOWING (Rabin-Karp, k=5, w=4)             │
         │ • Deteksi kecocokan verbatim kata-per-kata                            │
         │ • Jaccard Containment >= 80%  ──>  TAG MERAH (Copy-Paste)             │
         └───────────────────────────────────┬────────────────────────────────────┘
                                             │
                                             ▼
         ┌────────────────────────────────────────────────────────────────────────┐
         │ STEP 2: DETEKSI SEMANTIK SBERT + INDOBERT RE-RANKER (pgvector HNSW)   │
         │ • Dense Embedding 384-d (paraphrase-multilingual-MiniLM-L12-v2)       │
         │ • Kueri Jarak Kosinus (<=>) pada graf HNSW                            │
         │ • Re-ranker spesialis Indonesia: LazarusNLP/all-indobert-base-v4      │
         │ • Cosine Similarity >= 75%   ──>  TAG ORANYE (Parafrase Konsep)       │
         └───────────────────────────────────┬────────────────────────────────────┘
                                             │
                                             ▼
         ┌────────────────────────────────────────────────────────────────────────┐
         │ STEP 3: STILOMETRI & CONTEXTUAL AI JUDGE (Dual-Engine LLM)            │
         │ • Analisis Goh & Barabasi Burstiness B dan Type-Token Ratio (TTR)      │
         │ • Batch Prompt Verification: Google Gemini Flash / DeepSeek 9Router   │
         │ • Menyaring sitasi/istilah sah  ──>  TAG KUNING (Anomali AI)          │
         └───────────────────────────────────┬────────────────────────────────────┘
                                             │
                                             ▼
         ┌────────────────────────────────────────────────────────────────────────┐
         │ AGREGASI SKOR KOMPOSIT AKHIR                                           │
         │ Skor = (0.50 * Leksikal) + (0.35 * Semantik) + (0.15 * Stilometri)    │
         └───────────────────────────────────┬────────────────────────────────────┘
                                             │
                                             ▼
                     [ Interactive Heatmap Studio Workspace ]
```

---

## 2. Rincian Teknis per Tahap Komputasi

### 2.1. Step 1: Deteksi Leksikal Winnowing (Tag Merah)
* **Algoritma**: Winnowing Document Fingerprinting (Schleimer et al., 2003) dipadukan dengan Rabin-Karp Rolling Hash.
* **Parameter**:
  * Ukuran $k$-gram karakter: $k = 5$
  * Ukuran jendela luncur (*sliding window*): $w = 4$
  * Basis polinomial: $b = 257$
  * Modulus prima besar: $M = 1.000.000.007$
* **Kriteria Pelanggaran**:
  Kalimat naskah yang memiliki *Jaccard Containment* $\ge 80\%$ terhadap sidik jari pada tabel korpus ditandai sebagai **Tag Merah** (pelanggaran *copy-paste* verbatim).

### 2.2. Step 2: Deteksi Semantik SBERT & Re-ranker IndoBERT (Tag Oranye)
* **Tujuan**: Menangkap kalimat yang telah diubah sinonimnya atau direstrukturisasi, tetapi konsep dan maknanya tetap menjiplak sumber referensi.
* **Model Vektor Primer**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  * Menghasilkan representasi vektor padat 384 dimensi (`vector(384)`).
  * Diindeks menggunakan graf HNSW pada PostgreSQL pgvector dengan operator jarak kosinus (`<=>`).
  * **Implementasi (2026-11-08):** `engine/corpus_ann.py` (`PgvectorChunkSearch`) menjalankan `ORDER BY embedding <=> :vec LIMIT 1` per kalimat dengan `SET hnsw.ef_search = HNSW_EF_SEARCH` (default 64). Potongan korpus basis data tidak lagi dimuat ke memori; hanya korpus bawaan (`ReferenceCorpusBank`) yang dibandingkan di memori, lalu hasil terbaik dari keduanya dipakai. Bila basis data tidak tersedia, pencarian dimatikan untuk sisa audit dan sistem memakai korpus bawaan.
* **Re-ranker dua lapis**, dijalankan hanya pada kandidat yang lolos ambang 0,75:
  1. **Cross-encoder** `BAAI/bge-reranker-v2-m3` (ambang `RERANKER_THRESHOLD` = 0,5). Lapis ini yang menolak pasangan berlawanan makna.
  2. **IndoBERT** `LazarusNLP/all-indobert-base-v4` (768 dimensi, `engine/tier2_indobert.py`). Kosinus embedding harus minimal `INDOBERT_MIN_SIM` = 0,45. Catatan jujur: bi-encoder tidak bisa membedakan antonim (kosinus pasangan berlawanan makna pada set evaluasi 0,86 sampai 0,95), jadi lapis ini hanya ambang bawah untuk pasangan yang tidak berkaitan (kosinus maksimal 0,21 pada set evaluasi) dan tidak menaikkan akurasi set evaluasi 52 pasangan (tetap di atas 96%).
* **Kriteria Pelanggaran**:
  Kalimat yang memiliki skor kemiripan kosinus (*Cosine Similarity*) $\ge 0.75$ (75%) dan lolos verifikasi re-ranker ditandai sebagai **Tag Oranye** (parafrase konsep terdeteksi).

### 2.3. Step 3: Stilometri & Dual-Engine Contextual AI Judge (Tag Kuning)
* **Analisis Statistik Stilometri**:
  * Menghitung koefisien keanekaragaman panjang kalimat menggunakan metrik Goh & Barabasi Burstiness:
    $$B = \frac{\sigma_L - \mu_L}{\sigma_L + \mu_L}$$
  * Menghitung rasio kekayaan kosakata *Type-Token Ratio* (TTR). Teks cetakan mentah model bahasa AI (LLM) dicirikan oleh $B \approx -0.4$ s/d $0.0$ (monoton/seragam) dan TTR rendah.
* **Contextual AI Judge (Penyaring Sitasi Sah & Anomali)**:
  * Seluruh kandidat kalimat yang dicurigai dikelompokkan dalam **1 batch prompt terstruktur** ke lapisan LLM untuk mengevaluasi apakah kalimat merupakan kutipan langsung yang sah, peribahasa umum, atau teks hasil cetakan mesin.
  * Kalimat yang terkonfirmasi sebagai anomali sintaksis mesin ditandai sebagai **Tag Kuning**.

### 2.4. Formula Agregasi Skor Komposit
$$S_{\text{Composite}} = (0.50 \times S_{\text{Lexical}}) + (0.35 \times S_{\text{Semantic}}) + (0.15 \times S_{\text{Stylometric}})$$

Klasifikasi Skor Akhir Dokumen:
* **0% - 15% (Hijau)**: Aman (Tingkat orisinalitas tinggi).
* **16% - 30% (Oranye)**: Perlu Revisi Ringan (Terdapat parafrase yang perlu perbaikan sitasi).
* **> 30% (Merah)**: Plagiarisme Tinggi (Wajib parafrase sebelum publikasi/sidang).

---

## 3. Arsitektur Dual-Engine LLM Gateway (Automatic Failover)

Untuk menjamin ketersediaan sistem (*High Availability*) dan mencegah hambatan limit kuota (*Rate Limit 429*), lapisan LLM diimplementasikan menggunakan pola **Circuit Breaker / Adapter Pattern**:

```
                       [ Input Permintaan LLM: Judge / Chat / Paraphrase ]
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │     Dual-Engine LLM Gateway      │
                              └──────────────────────────────────┘
                                               │
                         ┌─────────────────────┴─────────────────────┐
                         ▼ (Mesin Primer)                            │
               ┌─────────────────────┐                               │
               │ Google Gemini Flash │                               │
               └─────────────────────┘                               │
                         │                                           │
          ┌──────────────┴──────────────┐                            │
          │                             │                            │
    [SUKSES 200]                   [GAGAL]                           │
          │             (Rate Limit 429 / 5xx Error)                 │
          │                             │                            │
          │                             ▼ (Failover Otomatis)        ▼ (Mesin Cadangan)
          │                   ┌────────────────────────────────────────┐
          │                   │   DeepSeek v4.1 Flash (via 9Router)    │
          │                   └────────────────────────────────────────┘
          │                                     │
          │                      ┌──────────────┴──────────────┐
          │                      │                             │
          │                [SUKSES 200]                   [GAGAL]
          │                      │                             │
          ▼                      ▼                             ▼
   [ Kembalikan Hasil Mulus ke Pengguna ]             [ Catat ke audit_logs ]
```

### Konfigurasi Lingkungan (`.env`)
```bash
# Strategi Gateway: "gemini_first" (default) atau "deepseek_first"
LLM_FAILOVER_STRATEGY=gemini_first

# Provider 1: Google Gemini Flash (AI Studio)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash

# Provider 2: DeepSeek via 9Router (Local Proxy)
ROUTER9_BASE_URL=http://localhost:20128/v1
ROUTER9_MODEL=deepseek/deepseek-v4.1-flash
ROUTER9_API_KEY=9router-local
```

### Strategi Penghematan Kuota (Anti-429 Batching)
Alih-alih mengirim kalimat satu per satu, modul Celery mengelompokkan maksimal 15 kalimat kandidat ke dalam 1 pesan JSON terstruktur. Dengan teknik ini:
* 1 dokumen naskah utuh hanya membutuhkan **1 hingga 2 panggilan API**.
* Kuota gratis Google AI Studio (1.500 panggilan per hari) mampu memproses hingga **750–1.500 dokumen per hari**, jauh melampaui kebutuhan pengujian dan demo tugas besar.

---

## 4. Sumber Korpus Otomatis (Dual-Scope)

Sistem VeriText AI tidak bergantung pada pengunggahan arsip ZIP manual. Basis data referensi diperbarui secara otomatis dari 6 sumber resmi:

1. **OpenAlex Academic Graph API**: Mengambil judul, abstrak, dan metadata karya ilmiah berbahasa Indonesia (`language:id`) dan internasional.
2. **Directory of Open Access Journals (DOAJ) API**: Menarik artikel jurnal ilmiah *open access* terindeks.
3. **Semantic Scholar Academic Graph API**: Mengambil ringkasan sitasi dan abstrak makalah ilmu komputer dan teknologi.
4. **Crossref REST API**: Mengidentifikasi metadata resmi DOI dan publikasi ilmiah berkala.
5. **HuggingFace Indonesian STS & Paraphrase Datasets**: Memuat dataset rujukan parafrase bahasa Indonesia (`jakartaresearch/id-paraphrase-detection`, `LazarusNLP/stsb_mt_id`).
6. **Google Search Grounding (Gemini)**: Verifikasi real-time terhadap rujukan artikel web publik terkini.
