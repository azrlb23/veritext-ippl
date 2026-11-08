import os
from diagram_builder import DrawioWriter, PngCanvas

DRAWIO_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/drawio"
EXPORT_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/exported"

AD_DATA = [
    {
        "id": "AD1",
        "title": "Aktivitas Masuk dan Registrasi Akun",
        "filename": "AD1-Masuk dan Registrasi Akun",
        "lanes": ["Pengguna (Free / Premium / Admin)", "Sistem VeriText AI (Frontend & Gateway)", "Google OAuth 2.0 & Database"],
        "height": 1050,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_pilih_metode", "type": "box", "lane": 0, "y": 140, "text": "Buka Halaman Masuk / Registrasi\ndan Pilih Metode Autentikasi"},
            {"id": "n_cek_metode", "type": "diamond", "lane": 1, "y": 230, "text": "Metode\nLogin?"},
            # Email branch
            {"id": "n_input_email", "type": "box", "lane": 0, "y": 320, "text": "Input Alamat Email &\nKata Sandi Akun"},
            {"id": "n_val_hash", "type": "box", "lane": 1, "y": 410, "text": "Validasi Format & Verifikasi\nHash Kata Sandi (Bcrypt)"},
            {"id": "n_cek_kredensial", "type": "diamond", "lane": 1, "y": 500, "text": "Kredensial\nValid?"},
            {"id": "n_err_login", "type": "box", "lane": 0, "y": 590, "text": "Tolak & Tampilkan Notifikasi:\n'Email atau Password Salah'"},
            {"id": "n_end_err", "type": "end", "lane": 0, "y": 660},
            {"id": "n_gen_jwt", "type": "box", "lane": 1, "y": 600, "text": "Generate JWT Access (15m) &\nRefresh Token (HttpOnly)"},
            {"id": "n_save_session", "type": "box", "lane": 2, "y": 700, "text": "Simpan Sesi Pengguna &\nCatat Audit Log Login"},
            {"id": "n_redirect_dash", "type": "box", "lane": 0, "y": 800, "text": "Arahkan ke Dasbor Workspace\n(Alokasi 5 Token & 3x Trial)"},
            {"id": "n_end_sukses", "type": "end", "lane": 0, "y": 880},
            # Google branch
            {"id": "n_consent_google", "type": "box", "lane": 2, "y": 320, "text": "Arahkan ke Google Consent Screen\n& Terima Callback Auth Code"},
            {"id": "n_tukar_token", "type": "box", "lane": 2, "y": 410, "text": "Tukar Auth Code dengan ID Token\n& Ekstrak Email Terverifikasi"}
        ],
        "edges": [
            ("n_start", "n_pilih_metode", "", None),
            ("n_pilih_metode", "n_cek_metode", "", None),
            ("n_cek_metode", "n_input_email", "[Email / Sandi]", None),
            ("n_cek_metode", "n_consent_google", "[Google OAuth]", None),
            ("n_consent_google", "n_tukar_token", "", None),
            ("n_tukar_token", "n_gen_jwt", "Profil Valid", None),
            ("n_input_email", "n_val_hash", "", None),
            ("n_val_hash", "n_cek_kredensial", "", None),
            ("n_cek_kredensial", "n_err_login", "[Tidak Valid]", None),
            ("n_err_login", "n_end_err", "", None),
            ("n_cek_kredensial", "n_gen_jwt", "[Valid]", None),
            ("n_gen_jwt", "n_save_session", "", None),
            ("n_save_session", "n_redirect_dash", "", None),
            ("n_redirect_dash", "n_end_sukses", "", None)
        ]
    },
    {
        "id": "AD2",
        "title": "Aktivitas Kelola Profil dan Kata Sandi",
        "filename": "AD2-Kelola Profil dan Kata Sandi",
        "lanes": ["Pengguna (Free / Premium)", "Sistem VeriText AI", "Database PostgreSQL"],
        "height": 1280,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_buka_menu", "type": "box", "lane": 0, "y": 140, "text": "Buka Menu Pengaturan Akun\ndan Pilih Tab Pengaturan"},
            {"id": "n_cek_tab", "type": "diamond", "lane": 1, "y": 230, "text": "Pilih Tab\nMenu?"},
            # Sub-flow 1: Profil (y = 320 s/d 660)
            {"id": "n_input_profil", "type": "box", "lane": 0, "y": 320, "text": "Input Nama Lengkap Baru /\nPreferensi Bahasa"},
            {"id": "n_sanitasi_profil", "type": "box", "lane": 1, "y": 410, "text": "Sanitasi String (Anti-XSS) &\nValidasi Format Data"},
            {"id": "n_update_db_profil", "type": "box", "lane": 2, "y": 500, "text": "Perbarui Record di Tabel users\ndan Terbitkan Sesi Baru"},
            {"id": "n_notif_profil", "type": "box", "lane": 0, "y": 590, "text": "Tampilkan Pesan Sukses:\n'Profil Berhasil Diperbarui'"},
            {"id": "n_end_profil", "type": "end", "lane": 0, "y": 660},
            # Sub-flow 2: Kata Sandi (y = 720 s/d 1180)
            {"id": "n_input_pwd", "type": "box", "lane": 0, "y": 720, "text": "Input Kata Sandi Lama &\nKata Sandi Baru (Min. 8 Karakter)"},
            {"id": "n_cek_pwd_lama", "type": "box", "lane": 1, "y": 810, "text": "Verifikasi Hash Bcrypt\nKata Sandi Lama"},
            {"id": "n_diamond_pwd", "type": "diamond", "lane": 1, "y": 900, "text": "Sandi Lama\nCocok?"},
            {"id": "n_err_pwd", "type": "box", "lane": 0, "y": 990, "text": "Tolak & Tampilkan Pesan:\n'Kata Sandi Lama Tidak Cocok'"},
            {"id": "n_end_pwd_err", "type": "end", "lane": 0, "y": 1060},
            {"id": "n_hash_new_pwd", "type": "box", "lane": 2, "y": 990, "text": "Hash Bcrypt Kata Sandi Baru &\nCabut Semua Sesi Aktif Lain"},
            {"id": "n_notif_pwd", "type": "box", "lane": 0, "y": 1100, "text": "Tampilkan Pesan Sukses:\n'Kata Sandi Berhasil Diperbarui'"},
            {"id": "n_end_pwd_sukses", "type": "end", "lane": 0, "y": 1180}
        ],
        "edges": [
            ("n_start", "n_buka_menu", "", None),
            ("n_buka_menu", "n_cek_tab", "", None),
            ("n_cek_tab", "n_input_profil", "[Tab Profil]", None),
            ("n_cek_tab", "n_input_pwd", "[Tab Sandi]", [(420, 230), (420, 720)]),
            ("n_input_profil", "n_sanitasi_profil", "", None),
            ("n_sanitasi_profil", "n_update_db_profil", "", None),
            ("n_update_db_profil", "n_notif_profil", "", None),
            ("n_notif_profil", "n_end_profil", "", None),
            ("n_input_pwd", "n_cek_pwd_lama", "", None),
            ("n_cek_pwd_lama", "n_diamond_pwd", "", None),
            ("n_diamond_pwd", "n_err_pwd", "[Tidak Cocok]", None),
            ("n_err_pwd", "n_end_pwd_err", "", None),
            ("n_diamond_pwd", "n_hash_new_pwd", "[Cocok]", None),
            ("n_hash_new_pwd", "n_notif_pwd", "", None),
            ("n_notif_pwd", "n_end_pwd_sukses", "", None)
        ]
    },
    {
        "id": "AD3",
        "title": "Aktivitas Unggah dan Validasi Naskah",
        "filename": "AD3-Unggah dan Validasi Naskah",
        "lanes": ["Pengguna (Free / Premium)", "Sistem VeriText AI (Frontend & Gateway)", "Storage & Preprocessor Engine"],
        "height": 1050,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_upload", "type": "box", "lane": 0, "y": 140, "text": "Unggah Berkas (.pdf/.docx/.txt)\natau Tempel Teks di Workspace"},
            {"id": "n_val_format", "type": "box", "lane": 1, "y": 230, "text": "Validasi Ekstensi, Ukuran (<=15MB)\n& Magic MIME-Type"},
            {"id": "n_cek_format", "type": "diamond", "lane": 1, "y": 320, "text": "Format &\nUkuran Valid?"},
            {"id": "n_err_format", "type": "box", "lane": 0, "y": 410, "text": "Tolak & Tampilkan Notifikasi:\n'Format Berkas Tidak Didukung / >15MB'"},
            {"id": "n_end_format_err", "type": "end", "lane": 0, "y": 480},
            {"id": "n_ekstrak_teks", "type": "box", "lane": 2, "y": 410, "text": "Ekstraksi Teks Bersih &\nHitung Jumlah Kata (word_count)"},
            {"id": "n_cek_role_cap", "type": "diamond", "lane": 1, "y": 510, "text": "Role Free &\nKata > 2.500?"},
            {"id": "n_err_free_cap", "type": "box", "lane": 0, "y": 600, "text": "Tampilkan Modal Paywall:\n'Free User Maksimal 2.500 Kata'"},
            {"id": "n_end_free_cap", "type": "end", "lane": 0, "y": 670},
            {"id": "n_hitung_token", "type": "box", "lane": 1, "y": 620, "text": "Kalkulasi Biaya Token Konsumsi:\nBiaya = min(5, ceil(kata / 2.500))"},
            {"id": "n_konfirmasi", "type": "box", "lane": 0, "y": 730, "text": "Tampilkan Pratinjau Naskah &\nKonfirmasi Pemotongan Token"},
            {"id": "n_end_upload", "type": "end", "lane": 0, "y": 820}
        ],
        "edges": [
            ("n_start", "n_upload", "", None),
            ("n_upload", "n_val_format", "", None),
            ("n_val_format", "n_cek_format", "", None),
            ("n_cek_format", "n_err_format", "[Tidak Valid]", None),
            ("n_err_format", "n_end_format_err", "", None),
            ("n_cek_format", "n_ekstrak_teks", "[Valid]", None),
            ("n_ekstrak_teks", "n_cek_role_cap", "", None),
            ("n_cek_role_cap", "n_err_free_cap", "[Ya, Overlimit]", None),
            ("n_err_free_cap", "n_end_free_cap", "", None),
            ("n_cek_role_cap", "n_hitung_token", "[Lolos / Premium]", None),
            ("n_hitung_token", "n_konfirmasi", "", None),
            ("n_konfirmasi", "n_end_upload", "", None)
        ]
    },
    {
        "id": "AD4",
        "title": "Aktivitas Deteksi Plagiarisme Hybrid 3-Tahap",
        "filename": "AD4-Deteksi Plagiarisme Hybrid 3-Tahap",
        "lanes": ["Pengguna (Free / Premium)", "Hybrid Audit Orchestrator", "Celery Worker, AI Engine & pgvector"],
        "height": 980,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_klik_periksa", "type": "box", "lane": 0, "y": 140, "text": "Klik Tombol 'Mulai Periksa Naskah'\nsetelah Review Estimasi Token"},
            {"id": "n_potong_token", "type": "box", "lane": 1, "y": 240, "text": "Validasi Saldo & Potong Token Atomik\nDispatch Task ke Antrean Celery"},
            {"id": "n_step1", "type": "box", "lane": 2, "y": 340, "text": "Step 1: Winnowing Lexical Match\n(Rabin-Karp Rolling Hash, Tag MERAH)"},
            {"id": "n_step2", "type": "box", "lane": 2, "y": 450, "text": "Step 2: Semantic SBERT + IndoBERT\n(Kueri KNN pgvector HNSW, Tag ORANYE)"},
            {"id": "n_step3", "type": "box", "lane": 2, "y": 560, "text": "Step 3: Stilometri (Burstiness, TTR)\n& Gemini Contextual AI Judge (Tag KUNING)"},
            {"id": "n_agregasi", "type": "box", "lane": 1, "y": 670, "text": "Kalkulasi Skor Komposit Akhir:\n(0.50 Leks + 0.35 Sem + 0.15 Stil)"},
            {"id": "n_tampil_hasil", "type": "box", "lane": 0, "y": 770, "text": "Render Interactive Heatmap &\nIndikator Persentase di Workspace"},
            {"id": "n_end_deteksi", "type": "end", "lane": 0, "y": 860}
        ],
        "edges": [
            ("n_start", "n_klik_periksa", "", None),
            ("n_klik_periksa", "n_potong_token", "", None),
            ("n_potong_token", "n_step1", "", None),
            ("n_step1", "n_step2", "", None),
            ("n_step2", "n_step3", "", None),
            ("n_step3", "n_agregasi", "", None),
            ("n_agregasi", "n_tampil_hasil", "", None),
            ("n_tampil_hasil", "n_end_deteksi", "", None)
        ]
    },
    {
        "id": "AD5",
        "title": "Aktivitas Tinjau Laporan dan Heatmap Kemiripan",
        "filename": "AD5-Tinjau Laporan dan Heatmap Kemiripan",
        "lanes": ["Pengguna (Free / Premium)", "Split-Screen Studio Workspace", "Database & Matched Source Store"],
        "height": 980,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_buka_hasil", "type": "box", "lane": 0, "y": 140, "text": "Buka Laporan Audit Naskah\npada Workspace Studio"},
            {"id": "n_ambil_data", "type": "box", "lane": 2, "y": 240, "text": "Ambil Rekaman Skor, Highlight Sentences,\ndan Sumber Pembanding dari Database"},
            {"id": "n_render_workspace", "type": "box", "lane": 1, "y": 340, "text": "Tampilkan Split-Screen Workspace:\nHeatmap Dokumen (Kiri) & Tab Sumber (Kanan)"},
            {"id": "n_klik_filter", "type": "box", "lane": 0, "y": 450, "text": "Pilih Filter Kategori Plagiat\n(Semua / Merah / Oranye / Kuning)"},
            {"id": "n_filter_view", "type": "box", "lane": 1, "y": 550, "text": "Perbarui Highlight Sesuai Filter &\nFokuskan ke Kalimat Bermasalah"},
            {"id": "n_klik_kalimat", "type": "box", "lane": 0, "y": 660, "text": "Klik Kalimat yang Disorot untuk\nMelihat Sumber Berdampingan"},
            {"id": "n_popover", "type": "box", "lane": 1, "y": 760, "text": "Buka Side-by-Side Comparison &\nTampilkan Opsi Aksi Asisten AI"},
            {"id": "n_end_tinjau", "type": "end", "lane": 0, "y": 850}
        ],
        "edges": [
            ("n_start", "n_buka_hasil", "", None),
            ("n_buka_hasil", "n_ambil_data", "", None),
            ("n_ambil_data", "n_render_workspace", "", None),
            ("n_render_workspace", "n_klik_filter", "", None),
            ("n_klik_filter", "n_filter_view", "", None),
            ("n_filter_view", "n_klik_kalimat", "", None),
            ("n_klik_kalimat", "n_popover", "", None),
            ("n_popover", "n_end_tinjau", "", None)
        ]
    },
    {
        "id": "AD6",
        "title": "Aktivitas Konsultasi Naskah via AI Chatbot",
        "filename": "AD6-Konsultasi Naskah via AI Chatbot",
        "lanes": ["Pengguna (Free / Premium)", "Academic Guardrail & Chat Service", "Gemini 2.5 Flash / OpenRouter API"],
        "height": 1050,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_buka_tab_chat", "type": "box", "lane": 0, "y": 140, "text": "Buka Tab 'AI Asisten' di Panel Kanan\ndan Masukkan Pertanyaan / Perintah"},
            {"id": "n_cek_kuota", "type": "diamond", "lane": 1, "y": 230, "text": "Status Kuota\nPengguna?"},
            {"id": "n_paywall_chat", "type": "box", "lane": 0, "y": 320, "text": "Tolak Permintaan & Tampilkan Paywall:\n'Trial 3x Habis, Silakan Beli Token'"},
            {"id": "n_end_trial_habis", "type": "end", "lane": 0, "y": 390},
            {"id": "n_guardrail", "type": "box", "lane": 1, "y": 340, "text": "Evaluasi Guardrail Akademik\n(Cek Relevansi Naskah & Anti-Joki)"},
            {"id": "n_cek_guardrail", "type": "diamond", "lane": 1, "y": 440, "text": "Lolos Guardrail\nAkademik?"},
            {"id": "n_tolak_guardrail", "type": "box", "lane": 0, "y": 530, "text": "Tolak & Tampilkan Notifikasi Error:\n'Permintaan di Luar Konteks Akademik'"},
            {"id": "n_end_guardrail_err", "type": "end", "lane": 0, "y": 600},
            {"id": "n_invoke_llm", "type": "box", "lane": 2, "y": 530, "text": "Kirim Konteks Kalimat Plagiat ke\nGemini 2.5 Flash / OpenRouter Fallback"},
            {"id": "n_potong_chat", "type": "box", "lane": 1, "y": 640, "text": "Kurangi Kuota Trial / Debet 0.1 Token &\nSimpan Log Percakapan ke Database"},
            {"id": "n_tampil_chat", "type": "box", "lane": 0, "y": 740, "text": "Tampilkan Respon Konsultasi Ilmiah\npada Panel Percakapan Chat"},
            {"id": "n_end_chat", "type": "end", "lane": 0, "y": 830}
        ],
        "edges": [
            ("n_start", "n_buka_tab_chat", "", None),
            ("n_buka_tab_chat", "n_cek_kuota", "", None),
            ("n_cek_kuota", "n_paywall_chat", "[Trial Habis]", None),
            ("n_paywall_chat", "n_end_trial_habis", "", None),
            ("n_cek_kuota", "n_guardrail", "[Kuota Ada]", None),
            ("n_guardrail", "n_cek_guardrail", "", None),
            ("n_cek_guardrail", "n_tolak_guardrail", "[Off-Topic]", None),
            ("n_tolak_guardrail", "n_end_guardrail_err", "", None),
            ("n_cek_guardrail", "n_invoke_llm", "[Valid Akademik]", None),
            ("n_invoke_llm", "n_potong_chat", "", None),
            ("n_potong_chat", "n_tampil_chat", "", None),
            ("n_tampil_chat", "n_end_chat", "", None)
        ]
    },
    {
        "id": "AD7",
        "title": "Aktivitas Parafrase Instan dan Cek Ulang Kalimat",
        "filename": "AD7-Parafrase Instan dan Cek Ulang Kalimat",
        "lanes": ["Pengguna (Free / Premium)", "Paraphrase Engine & Workspace", "Gemini AI Engine & Audit Orchestrator"],
        "height": 1050,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_pilih_mode_para", "type": "box", "lane": 0, "y": 140, "text": "Pilih Kalimat/Paragraf di Heatmap &\nKlik 'Parafrase Kalimat / Paragraf / Halaman'"},
            {"id": "n_cek_token_para", "type": "diamond", "lane": 1, "y": 230, "text": "Kredit AI\nMencukupi?"},
            {"id": "n_modal_topup_para", "type": "box", "lane": 0, "y": 320, "text": "Tampilkan Notifikasi 'Saldo Kurang'\n& Arahkan ke Menu Beli Token"},
            {"id": "n_end_para_token_err", "type": "end", "lane": 0, "y": 390},
            {"id": "n_gen_3opsi", "type": "box", "lane": 2, "y": 320, "text": "Hasilkan 3 Opsi Variasi Parafrase Ilmiah\nlengkap dengan Estimasi Penurunan Skor"},
            {"id": "n_pilih_opsi", "type": "box", "lane": 0, "y": 430, "text": "Tinjau 3 Opsi di Panel Kanan &\nPilih 1 Variasi Terbaik"},
            {"id": "n_apply_rescore", "type": "box", "lane": 1, "y": 530, "text": "Perbarui Teks Naskah Secara In-Place\ndan Hitung Ulang Skor Kemiripan"},
            {"id": "n_save_db_para", "type": "box", "lane": 2, "y": 630, "text": "Simpan Perubahan ke Database &\nUbah Sorotan Kalimat Menjadi Hijau"},
            {"id": "n_tampil_skor_baru", "type": "box", "lane": 0, "y": 730, "text": "Tampilkan Naskah yang Telah Diperbaiki\ndan Skor Plagiarisme yang Telah Turun"},
            {"id": "n_end_para", "type": "end", "lane": 0, "y": 820}
        ],
        "edges": [
            ("n_start", "n_pilih_mode_para", "", None),
            ("n_pilih_mode_para", "n_cek_token_para", "", None),
            ("n_cek_token_para", "n_modal_topup_para", "[Tidak Cukup]", None),
            ("n_modal_topup_para", "n_end_para_token_err", "", None),
            ("n_cek_token_para", "n_gen_3opsi", "[Cukup]", None),
            ("n_gen_3opsi", "n_pilih_opsi", "", None),
            ("n_pilih_opsi", "n_apply_rescore", "", None),
            ("n_apply_rescore", "n_save_db_para", "", None),
            ("n_save_db_para", "n_tampil_skor_baru", "", None),
            ("n_tampil_skor_baru", "n_end_para", "", None)
        ]
    },
    {
        "id": "AD8",
        "title": "Aktivitas Unduh Laporan PDF dan Verifikasi QR",
        "filename": "AD8-Unduh Laporan PDF dan Verifikasi QR",
        "lanes": ["Pengguna (Free / Premium / Publik)", "Sistem VeriText AI (Report & QR API)", "PDF Generator & Public QR Verifier"],
        "height": 1150,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_pilih_aksi_rep", "type": "box", "lane": 0, "y": 140, "text": "Pilih Aksi: Unduh Laporan PDF Resmi\natau Pindai Kode QR Verifikasi"},
            {"id": "n_cek_jenis_rep", "type": "diamond", "lane": 1, "y": 230, "text": "Pilih Jenis\nLayanan?"},
            # Sub-flow A: Unduh PDF (y = 320 s/d 600)
            {"id": "n_cek_role_pdf", "type": "diamond", "lane": 1, "y": 320, "text": "Role Akun\n== 'PREMIUM'?"},
            {"id": "n_paywall_pdf", "type": "box", "lane": 0, "y": 410, "text": "Tolak Unduh PDF: 'Fitur Khusus\nPengguna Premium' (+ Paywall)"},
            {"id": "n_end_pdf_err", "type": "end", "lane": 0, "y": 480},
            {"id": "n_build_pdf", "type": "box", "lane": 2, "y": 410, "text": "Generate Dokumen PDF Resmi Lengkap\ndengan Barcode QR Code Verifikasi"},
            {"id": "n_download_pdf", "type": "box", "lane": 0, "y": 520, "text": "Unduh Berkas Laporan PDF Resmi\nke Penyimpanan Lokal Pengguna"},
            {"id": "n_end_pdf_sukses", "type": "end", "lane": 0, "y": 600},
            # Sub-flow B: Verifikasi QR Publik (y = 680 s/d 960)
            {"id": "n_scan_qr", "type": "box", "lane": 0, "y": 680, "text": "Pindai Kode QR pada Berkas PDF\n(Arahkan URL ke /verify/{uuid})"},
            {"id": "n_lookup_qr", "type": "box", "lane": 2, "y": 770, "text": "Cari Metadata Sertifikat Asli di Database\n(Pencocokan UUID Sertifikat)"},
            {"id": "n_tampil_verif", "type": "box", "lane": 0, "y": 870, "text": "Tampilkan Halaman Verifikasi Publik:\nStatus Sah, Pemilik & Skor Asli"},
            {"id": "n_end_verif", "type": "end", "lane": 0, "y": 950}
        ],
        "edges": [
            ("n_start", "n_pilih_aksi_rep", "", None),
            ("n_pilih_aksi_rep", "n_cek_jenis_rep", "", None),
            ("n_cek_jenis_rep", "n_cek_role_pdf", "[Unduh PDF]", None),
            ("n_cek_jenis_rep", "n_scan_qr", "[Verifikasi QR]", [(420, 230), (420, 680)]),
            ("n_cek_role_pdf", "n_paywall_pdf", "[Free User]", None),
            ("n_paywall_pdf", "n_end_pdf_err", "", None),
            ("n_cek_role_pdf", "n_build_pdf", "[Premium]", None),
            ("n_build_pdf", "n_download_pdf", "", None),
            ("n_download_pdf", "n_end_pdf_sukses", "", None),
            ("n_scan_qr", "n_lookup_qr", "", None),
            ("n_lookup_qr", "n_tampil_verif", "", None),
            ("n_tampil_verif", "n_end_verif", "", None)
        ]
    },
    {
        "id": "AD9",
        "title": "Aktivitas Kelola dan Hapus Riwayat Naskah",
        "filename": "AD9-Kelola dan Hapus Riwayat Naskah",
        "lanes": ["Pengguna (Free / Premium)", "Sistem VeriText AI", "Storage & Database (UU PDP)"],
        "height": 950,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_buka_riwayat", "type": "box", "lane": 0, "y": 140, "text": "Buka Halaman Riwayat Naskah\ndan Pilih Dokumen yang Ingin Dihapus"},
            {"id": "n_klik_hapus", "type": "box", "lane": 0, "y": 240, "text": "Klik Tombol 'Hapus Permanen'\ndan Konfirmasi Modal Peringatan"},
            {"id": "n_val_owner", "type": "box", "lane": 1, "y": 340, "text": "Validasi Kepemilikan Dokumen\n(Pencocokan user_id Pemilik)"},
            {"id": "n_hard_delete", "type": "box", "lane": 2, "y": 450, "text": "Eksekusi Hard-Delete Cascade:\nHapus File Fisik, Hasil Audit & Chat"},
            {"id": "n_catat_audit_pdp", "type": "box", "lane": 1, "y": 560, "text": "Catat Peristiwa Penghapusan pada\nLog Audit (Kepatuhan UU PDP No. 27/2022)"},
            {"id": "n_notif_delete", "type": "box", "lane": 0, "y": 670, "text": "Tampilkan Pesan Sukses:\n'Dokumen Telah Dihapus Permanen'"},
            {"id": "n_end_delete", "type": "end", "lane": 0, "y": 760}
        ],
        "edges": [
            ("n_start", "n_buka_riwayat", "", None),
            ("n_buka_riwayat", "n_klik_hapus", "", None),
            ("n_klik_hapus", "n_val_owner", "", None),
            ("n_val_owner", "n_hard_delete", "", None),
            ("n_hard_delete", "n_catat_audit_pdp", "", None),
            ("n_catat_audit_pdp", "n_notif_delete", "", None),
            ("n_notif_delete", "n_end_delete", "", None)
        ]
    },
    {
        "id": "AD10",
        "title": "Aktivitas Beli Kuota Token dan Upgrade Premium",
        "filename": "AD10-Beli Kuota Token dan Upgrade Premium",
        "lanes": ["Pengguna (Free / Premium)", "Sistem VeriText AI & Webhook", "Midtrans Payment Gateway"],
        "height": 1050,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_buka_topup", "type": "box", "lane": 0, "y": 140, "text": "Buka Menu Billing & Top-Up Kuota,\nPilih Skema: By Token atau Paket Token"},
            {"id": "n_create_invoice", "type": "box", "lane": 1, "y": 240, "text": "Validasi Input (Min. 5 Token) &\nBuat Record Invoice PENDING di Database"},
            {"id": "n_request_snap", "type": "box", "lane": 2, "y": 340, "text": "Request Snap Token ke Midtrans API &\nTampilkan Pop-up Pembayaran Snap"},
            {"id": "n_bayar_snap", "type": "box", "lane": 0, "y": 450, "text": "Pilih Metode (QRIS, VA, Kartu)\ndan Selesaikan Pembayaran"},
            {"id": "n_midtrans_webhook", "type": "box", "lane": 2, "y": 560, "text": "Kirim HTTP POST Webhook Notifikasi\n(Signature Key SHA-512)"},
            {"id": "n_proses_webhook", "type": "box", "lane": 1, "y": 670, "text": "Verifikasi Signature, Tambah Saldo Token\n& Auto-Upgrade Role -> 'PREMIUM'"},
            {"id": "n_tampil_lunas", "type": "box", "lane": 0, "y": 780, "text": "Tampilkan Status Lunas, Saldo Baru,\ndan Tombol Unduh Invoice PDF"},
            {"id": "n_end_topup", "type": "end", "lane": 0, "y": 870}
        ],
        "edges": [
            ("n_start", "n_buka_topup", "", None),
            ("n_buka_topup", "n_create_invoice", "", None),
            ("n_create_invoice", "n_request_snap", "", None),
            ("n_request_snap", "n_bayar_snap", "", None),
            ("n_bayar_snap", "n_midtrans_webhook", "", None),
            ("n_midtrans_webhook", "n_proses_webhook", "", None),
            ("n_proses_webhook", "n_tampil_lunas", "", None),
            ("n_tampil_lunas", "n_end_topup", "", None)
        ]
    },
    {
        "id": "AD11",
        "title": "Aktivitas Pantau Dasbor Analitik dan Log Transaksi",
        "filename": "AD11-Pantau Dasbor Analitik dan Log Transaksi",
        "lanes": ["Admin (100% Read-Only)", "Admin Gateway Service", "Database & Telemetri Server"],
        "height": 950,
        "nodes": [
            {"id": "n_start", "type": "start", "lane": 0, "y": 70},
            {"id": "n_login_admin", "type": "box", "lane": 0, "y": 140, "text": "Masuk dengan Akun Admin &\nBuka Halaman Dasbor Analitik"},
            {"id": "n_val_admin_role", "type": "box", "lane": 1, "y": 240, "text": "Validasi Token JWT & Otorisasi\nRole == 'ADMIN' (Read-Only Guard)"},
            {"id": "n_kueri_agregasi", "type": "box", "lane": 2, "y": 340, "text": "Eksekusi Kueri Agregasi SELECT:\nTotal Audit, Tren Skor, & Total Revenue"},
            {"id": "n_sajikan_telemetri", "type": "box", "lane": 1, "y": 450, "text": "Sajikan Data Telemetri, Status Worker,\ndan Riwayat Transaksi Midtrans"},
            {"id": "n_amati_grafik", "type": "box", "lane": 0, "y": 560, "text": "Amati Grafik & Terapkan Filter Tanggal\n(Murni Observasi Tanpa Mutasi Data)"},
            {"id": "n_end_admin", "type": "end", "lane": 0, "y": 650}
        ],
        "edges": [
            ("n_start", "n_login_admin", "", None),
            ("n_login_admin", "n_val_admin_role", "", None),
            ("n_val_admin_role", "n_kueri_agregasi", "", None),
            ("n_kueri_agregasi", "n_sajikan_telemetri", "", None),
            ("n_sajikan_telemetri", "n_amati_grafik", "", None),
            ("n_amati_grafik", "n_end_admin", "", None)
        ]
    }
]

def render_ad(item):
    name = item["filename"]
    max_node_y = max(n["y"] for n in item["nodes"])
    dw_h = max(max_node_y + 90, 700)
    dw = DrawioWriter(f"dw_{item['id'].lower()}", item["title"], width=1200, height=dw_h)
    canvas = PngCanvas(width=1200, height=dw_h, scale=2)

    lanes = item["lanes"]
    lane_w = 360
    start_x = 60
    total_w = lane_w * len(lanes)

    # 1. Draw Swimlanes (Strictly Black & White)
    dw.add_node(f"pool_{item['id']}", item['title'], start_x, 30, total_w, dw_h - 60,
                "swimlane;html=1;childLayout=stackLayout;startSize=28;horizontal=0;horizontalStack=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;fontStyle=1;fontSize=12;fontColor=#000000;")

    for i, lane_title in enumerate(lanes):
        lx = start_x + i * lane_w
        canvas.draw_swimlane(lx, 30, lane_w, dw_h - 60, lane_title, fill="#FFFFFF", header_fill="#FFFFFF")
        dw.add_node(f"lane_{i}", lane_title, lx, 30, lane_w, dw_h - 60,
                    "swimlane;html=1;startSize=28;horizontal=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontStyle=1;fontSize=11;fontColor=#000000;")

    # 2. Render Nodes
    node_coords = {}
    bw, bh = 240, 50

    for n in item["nodes"]:
        nid = n["id"]
        ntype = n["type"]
        l_idx = n["lane"]
        cx = start_x + l_idx * lane_w + lane_w / 2
        cy = n["y"]
        node_coords[nid] = (cx, cy, ntype)

        if ntype == "start":
            canvas.draw_start_node(cx, cy, r=12)
            dw.add_node(nid, "", cx - 12, cy - 12, 24, 24, "ellipse;shape=startState;fillColor=#000000;strokeColor=none;")
        elif ntype == "end":
            canvas.draw_end_node(cx, cy, r=12)
            dw.add_node(nid, "", cx - 12, cy - 12, 24, 24, "ellipse;shape=endState;fillColor=#000000;strokeColor=#000000;")
        elif ntype == "diamond":
            canvas.draw_diamond(cx - 55, cy - 26, 110, 52, n["text"], fill="#FFFFFF", stroke="#000000", stroke_width=1.5, font_size=9.5)
            dw.add_node(nid, n["text"], cx - 55, cy - 26, 110, 52, "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=9.5;fontStyle=1;align=center;")
        elif ntype == "box":
            canvas.draw_box(cx - bw/2, cy - bh/2, bw, bh, n["text"], fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=6, font_size=9.5)
            dw.add_node(nid, n["text"], cx - bw/2, cy - bh/2, bw, bh, "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;align=center;")

    # 3. Render Directed Orthogonal Edges (Clean non-overlapping routing)
    for edge_idx, edge_data in enumerate(item["edges"]):
        src_id, tgt_id, lbl = edge_data[0], edge_data[1], edge_data[2]
        custom_pts = edge_data[3] if len(edge_data) > 3 else None

        src_cx, src_cy, src_type = node_coords[src_id]
        tgt_cx, tgt_cy, tgt_type = node_coords[tgt_id]

        src_h = 24 if src_type in ["start", "end"] else (52 if src_type == "diamond" else bh)
        tgt_h = 24 if tgt_type in ["start", "end"] else (52 if tgt_type == "diamond" else bh)
        src_w = 24 if src_type in ["start", "end"] else (110 if src_type == "diamond" else bw)
        tgt_w = 24 if tgt_type in ["start", "end"] else (110 if tgt_type == "diamond" else bw)

        if custom_pts:
            # Explicit obstacle-avoiding waypoints
            start_pt = (src_cx + (src_w/2 if custom_pts[0][0] > src_cx else -src_w/2) if src_type == "diamond" else src_cx,
                        src_cy if src_type == "diamond" else src_cy + src_h/2)
            exit_style = ("exitX=1;exitY=0.5;exitDx=0;exitDy=0;" if custom_pts[0][0] > src_cx else "exitX=0;exitY=0.5;exitDx=0;exitDy=0;") if src_type == "diamond" else "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
            
            last_pt = custom_pts[-1]
            if abs(last_pt[1] - tgt_cy) < 5:
                if last_pt[0] > tgt_cx:
                    end_pt = (tgt_cx + tgt_w/2, tgt_cy)
                    entry_style = "entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
                else:
                    end_pt = (tgt_cx - tgt_w/2, tgt_cy)
                    entry_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
            else:
                end_pt = (tgt_cx, tgt_cy - tgt_h/2)
                entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"

            pts = [start_pt] + custom_pts + [end_pt]
            canvas.draw_polyline_arrow(pts, label=lbl, color="#000000", stroke_width=1.5)
            dw.add_edge(f"e_{edge_idx}", src_id, tgt_id, lbl, f"edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.5;endArrow=block;{exit_style}{entry_style}", waypoints=custom_pts)
        elif abs(src_cx - tgt_cx) < 5 and src_cy < tgt_cy:
            # Straight down in same lane
            y1 = src_cy + src_h / 2
            y2 = tgt_cy - tgt_h / 2
            canvas.draw_arrow(src_cx, y1, src_cx, y2, label=lbl, color="#000000", stroke_width=1.5)
            dw.add_edge(f"e_{edge_idx}", src_id, tgt_id, lbl, "strokeColor=#000000;strokeWidth=1.5;endArrow=block;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
        elif src_type == "diamond":
            # Exit sideways from diamond tip into top of target
            exit_x = src_cx + (src_w / 2 if tgt_cx > src_cx else -src_w / 2)
            exit_y = src_cy
            exit_style = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;" if tgt_cx > src_cx else "exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
            entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
            pts = [(exit_x, exit_y), (tgt_cx, exit_y), (tgt_cx, tgt_cy - tgt_h / 2)]
            waypoints = [(tgt_cx, exit_y)]
            canvas.draw_polyline_arrow(pts, label=lbl, color="#000000", stroke_width=1.5)
            dw.add_edge(f"e_{edge_idx}", src_id, tgt_id, lbl, f"edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.5;endArrow=block;{exit_style}{entry_style}", waypoints=waypoints)
        elif src_cx > tgt_cx:
            # Right-to-Left box: exit bottom, drop in source lane down to tgt_cy, enter right face of target
            exit_x = src_cx
            exit_y = src_cy + src_h / 2
            entry_x = tgt_cx + tgt_w / 2
            entry_y = tgt_cy
            exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
            entry_style = "entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
            pts = [(exit_x, exit_y), (exit_x, entry_y), (entry_x, entry_y)]
            waypoints = [(exit_x, entry_y)]
            canvas.draw_polyline_arrow(pts, label=lbl, color="#000000", stroke_width=1.5)
            dw.add_edge(f"e_{edge_idx}", src_id, tgt_id, lbl, f"edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.5;endArrow=block;{exit_style}{entry_style}", waypoints=waypoints)
        else:
            # Left-to-Right box: exit bottom, drop to y_mid, enter top of target
            exit_x = src_cx
            exit_y = src_cy + src_h / 2
            y_mid = (exit_y + tgt_cy - tgt_h / 2) / 2
            exit_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
            entry_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
            pts = [(exit_x, exit_y), (exit_x, y_mid), (tgt_cx, y_mid), (tgt_cx, tgt_cy - tgt_h / 2)]
            waypoints = [(exit_x, y_mid), (tgt_cx, y_mid)]
            canvas.draw_polyline_arrow(pts, label=lbl, color="#000000", stroke_width=1.5)
            dw.add_edge(f"e_{edge_idx}", src_id, tgt_id, lbl, f"edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.5;endArrow=block;{exit_style}{entry_style}", waypoints=waypoints)

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")

def main():
    for item in AD_DATA:
        render_ad(item)

if __name__ == "__main__":
    main()
