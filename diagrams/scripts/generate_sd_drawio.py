import os
from diagram_builder import DrawioWriter, PngCanvas

DRAWIO_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/drawio"
EXPORT_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/exported"

SD_DATA = [
    {
        "id": "SD1",
        "title": "Sequence Diagram: Masuk dan Registrasi Akun",
        "filename": "SD1-Masuk dan Registrasi Akun",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":AuthView\n(Vue 3)"),
            ("api", ":AuthAPI\n(FastAPI)"),
            ("srv", ":AuthService"),
            ("db", ":PostgreSQL\n(users, sessions)"),
            ("oauth", ":GoogleOAuth\n(Google API)")
        ],
        "messages": [
            (0, 1, "1. Masukkan email & password", "sync"),
            (1, 2, "2. POST /api/v1/auth/login", "sync"),
            (2, 3, "3. authenticate_user(email, password)", "sync"),
            (3, 4, "4. SELECT * FROM users WHERE email", "sync"),
            (4, 3, "5. Data user & password_hash", "ret"),
            (3, 3, "6. Verifikasi bcrypt hash", "self"),
            (3, 4, "7. INSERT INTO sessions (refresh_token)", "sync"),
            (3, 2, "8. UserPayload + AccessToken JWT", "ret"),
            (2, 1, "9. 200 OK (Set HttpOnly Cookie & JWT)", "ret"),
            (1, 0, "10. Redirect ke /workspace (Dasbor)", "ret"),
            (0, 1, "11. [Alt] Klik 'Masuk dengan Google'", "sync"),
            (1, 5, "12. Redirect ke Google Consent Screen", "sync"),
            (5, 1, "13. Callback auth dengan auth_code", "ret"),
            (1, 2, "14. POST /api/v1/auth/google/callback", "sync"),
            (2, 5, "15. Tukar code dengan ID Token", "sync"),
            (5, 2, "16. User profile terverifikasi", "ret"),
            (2, 4, "17. Upsert user (Alokasi 5 Token & 3x Trial)", "sync"),
            (2, 1, "18. 200 OK (JWT Session Active)", "ret"),
            (1, 0, "19. Redirect ke /workspace", "ret")
        ]
    },
    {
        "id": "SD2",
        "title": "Sequence Diagram: Kelola Profil dan Kata Sandi",
        "filename": "SD2-Kelola Profil dan Kata Sandi",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":ProfileSettings\n(Vue 3)"),
            ("api", ":UserAPI\n(FastAPI)"),
            ("srv", ":UserService"),
            ("db", ":PostgreSQL\n(users)")
        ],
        "messages": [
            (0, 1, "1. Input Nama Baru / Ubah Preferensi", "sync"),
            (1, 2, "2. PUT /api/v1/users/profile (Bearer JWT)", "sync"),
            (2, 3, "3. update_profile(user_id, schema)", "sync"),
            (3, 4, "4. UPDATE users SET full_name = ...", "sync"),
            (4, 3, "5. Rows updated successfully", "ret"),
            (3, 2, "6. UserResponse updated", "ret"),
            (2, 1, "7. 200 OK (Profile Updated)", "ret"),
            (1, 0, "8. Notifikasi 'Profil berhasil diperbarui'", "ret"),
            (0, 1, "9. [Alt] Input Kata Sandi Lama & Baru", "sync"),
            (1, 2, "10. POST /api/v1/users/change-password", "sync"),
            (2, 3, "11. verify_old_and_hash_new()", "sync"),
            (3, 4, "12. SELECT password_hash FROM users", "sync"),
            (4, 3, "13. Hash cocok", "ret"),
            (3, 4, "14. UPDATE users SET password_hash, revoke sessions", "sync"),
            (4, 3, "15. Sesi lama dicabut", "ret"),
            (3, 2, "16. Password update success", "ret"),
            (2, 1, "17. 200 OK (Sandi Diperbarui)", "ret"),
            (1, 0, "18. Notifikasi 'Kata sandi berhasil diubah'", "ret")
        ]
    },
    {
        "id": "SD3",
        "title": "Sequence Diagram: Unggah dan Validasi Naskah",
        "filename": "SD3-Unggah dan Validasi Naskah",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":WorkspaceView\n(Split-Screen)"),
            ("api", ":DocumentAPI\n(FastAPI)"),
            ("prep", ":PreprocessorEngine"),
            ("wallet", ":TokenWalletService"),
            ("db", ":PostgreSQL\n(documents)")
        ],
        "messages": [
            (0, 1, "1. Unggah berkas / tempel teks", "sync"),
            (1, 2, "2. POST /api/v1/documents/upload", "sync"),
            (2, 3, "3. validate_and_extract_text(file)", "sync"),
            (3, 3, "4. Cek MIME magic, limit <=15MB, ekstrak teks", "self"),
            (3, 3, "5. Hitung kata naskah: word_count", "self"),
            (3, 2, "6. TextPayload (clean_text, word_count)", "ret"),
            (2, 4, "7. calculate_token_cost(role, word_count)", "sync"),
            (4, 4, "8. Formula: min(5, ceil(kata / 2500))", "self"),
            (4, 2, "9. Estimasi biaya token", "ret"),
            (2, 5, "10. INSERT INTO documents (title, path, words)", "sync"),
            (5, 2, "11. Document created (uuid)", "ret"),
            (2, 1, "12. 201 Created (doc_id, words, token_cost)", "ret"),
            (1, 0, "13. Tampilkan pratinjau & konfirmasi biaya", "ret")
        ]
    },
    {
        "id": "SD4",
        "title": "Sequence Diagram: Deteksi Plagiarisme Hybrid 3-Tahap",
        "filename": "SD4-Deteksi Plagiarisme Hybrid 3-Tahap",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":WorkspaceView"),
            ("orch", ":AuditOrchestrator"),
            ("step1", ":WinnowingEngine"),
            ("step2", ":SemanticVectorEngine"),
            ("step3", ":StylometricAIEngine"),
            ("db", ":pgvector & DB")
        ],
        "messages": [
            (0, 1, "1. Klik 'Mulai Periksa Naskah'", "sync"),
            (1, 2, "2. POST /api/v1/audits/execute (doc_id)", "sync"),
            (2, 6, "3. Potong saldo token secara atomik", "sync"),
            (2, 3, "4. run_step1_lexical(clean_text)", "sync"),
            (3, 6, "5. Cek hash fingerprint (Rabin-Karp)", "sync"),
            (6, 3, "6. Matched lexical fingerprints (Red)", "ret"),
            (3, 2, "7. LexicalScore + RedHighlights", "ret"),
            (2, 4, "8. run_step2_semantic(chunks)", "sync"),
            (4, 6, "9. KNN Cosine search (<=>) HNSW", "sync"),
            (6, 4, "10. Matched vector chunks (Orange)", "ret"),
            (4, 2, "11. SemanticScore + OrangeHighlights", "ret"),
            (2, 5, "12. run_step3_stylometric(text)", "sync"),
            (5, 5, "13. Hitung Burstiness B & TTR ratio", "self"),
            (5, 2, "14. StylometricScore + YellowHighlights", "ret"),
            (2, 2, "15. Agregasi skor komposit (0.50 : 0.35 : 0.15)", "self"),
            (2, 6, "16. Simpan AuditReport & AuditSentences", "sync"),
            (2, 1, "17. 200 OK (Task Completed, audit_id)", "ret"),
            (1, 0, "18. Render Interactive Heatmap di Workspace", "ret")
        ]
    },
    {
        "id": "SD5",
        "title": "Sequence Diagram: Tinjau Laporan dan Heatmap Kemiripan",
        "filename": "SD5-Tinjau Laporan dan Heatmap Kemiripan",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":WorkspaceView\n(Split-Screen)"),
            ("api", ":ReportAPI\n(FastAPI)"),
            ("db", ":PostgreSQL\n(reports, sentences)")
        ],
        "messages": [
            (0, 1, "1. Buka laporan hasil audit naskah", "sync"),
            (1, 2, "2. GET /api/v1/audits/{id}/report", "sync"),
            (2, 3, "3. SELECT * FROM audit_reports WHERE id", "sync"),
            (3, 2, "4. Record report & skor komposit", "ret"),
            (2, 3, "5. SELECT * FROM audit_sentences WHERE task_id", "sync"),
            (3, 2, "6. Array 3-tier highlighted sentences", "ret"),
            (2, 1, "7. 200 OK (ReportDetailsPayload)", "ret"),
            (1, 0, "8. Tampilkan Heatmap (Kiri) & Sumber (Kanan)", "ret"),
            (0, 1, "9. Klik filter tag 'Merah - Leksikal'", "sync"),
            (1, 1, "10. Filter highlight & fokuskan kalimat terpilih", "self"),
            (0, 1, "11. Klik kalimat bermasalah", "sync"),
            (1, 0, "12. Tampilkan popover Side-by-Side comparison", "ret")
        ]
    },
    {
        "id": "SD6",
        "title": "Sequence Diagram: Konsultasi Naskah via AI Chatbot",
        "filename": "SD6-Konsultasi Naskah via AI Chatbot",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":ChatPanel\n(Tab 2 Workspace)"),
            ("api", ":ChatAPI\n(FastAPI)"),
            ("guard", ":AcademicGuardrail"),
            ("llm", ":GeminiAIService"),
            ("db", ":PostgreSQL\n(chat_sessions)")
        ],
        "messages": [
            (0, 1, "1. Ketik pertanyaan / klik quick prompt", "sync"),
            (1, 2, "2. POST /api/v1/chat/message (doc_id, query)", "sync"),
            (2, 5, "3. Cek kuota token / status trial pengguna", "sync"),
            (5, 2, "4. Sisa kuota valid", "ret"),
            (2, 3, "5. validate_scope(query, sentence_context)", "sync"),
            (3, 2, "6. Valid akademik (Lolos guardrail)", "ret"),
            (2, 4, "7. generate_academic_guidance(context, prompt)", "sync"),
            (4, 2, "8. Jawaban konsultasi & saran sitasi", "ret"),
            (2, 5, "9. INSERT INTO chat_messages, potong 0.1 token", "sync"),
            (5, 2, "10. Message logged & balance updated", "ret"),
            (2, 1, "11. 200 OK (ChatResponsePayload)", "ret"),
            (1, 0, "12. Render balon percakapan di ChatPanel", "ret")
        ]
    },
    {
        "id": "SD7",
        "title": "Sequence Diagram: Parafrase Instan dan Cek Ulang Kalimat",
        "filename": "SD7-Parafrase Instan dan Cek Ulang Kalimat",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":WorkspaceView"),
            ("api", ":ParaphraseAPI"),
            ("llm", ":GeminiAIService"),
            ("orch", ":AuditOrchestrator"),
            ("db", ":PostgreSQL")
        ],
        "messages": [
            (0, 1, "1. Klik 'Parafrase Kalimat Ini' (Mode Per Kalimat)", "sync"),
            (1, 2, "2. POST /api/v1/chat/paraphrase (sentence_id, mode)", "sync"),
            (2, 3, "3. generate_3_academic_variations(text)", "sync"),
            (3, 2, "4. 3 opsi variasi + estimasi skor", "ret"),
            (2, 1, "5. 200 OK (OptionsPayload)", "ret"),
            (1, 0, "6. Tampilkan kartu pilihan 3 opsi parafrase", "ret"),
            (0, 1, "7. Pilih Opsi #2 & klik 'Terapkan ke Naskah'", "sync"),
            (1, 2, "8. POST /api/v1/chat/apply-paraphrase", "sync"),
            (2, 4, "9. recompute_sentence_score(new_text)", "sync"),
            (4, 2, "10. Skor baru turun: 88% -> 8% (Lolos)", "ret"),
            (2, 5, "11. UPDATE audit_sentences SET in-place text & tag", "sync"),
            (5, 2, "12. Record updated", "ret"),
            (2, 1, "13. 200 OK (UpdatedSentence & NewScore)", "ret"),
            (1, 0, "14. Ubah highlight jadi Hijau & turunkan skor total", "ret")
        ]
    },
    {
        "id": "SD8",
        "title": "Sequence Diagram: Unduh Laporan PDF dan Verifikasi QR",
        "filename": "SD8-Unduh Laporan PDF dan Verifikasi QR",
        "participants": [
            ("user", "User / Publik"),
            ("view", ":BrowserClient"),
            ("api", ":ReportAPI\n(FastAPI)"),
            ("pdf", ":ReportGeneratorService"),
            ("db", ":PostgreSQL")
        ],
        "messages": [
            (0, 1, "1. Klik 'Unduh Laporan PDF'", "sync"),
            (1, 2, "2. GET /api/v1/reports/{id}/download (Bearer JWT)", "sync"),
            (2, 4, "3. Cek role user == 'PREMIUM'", "sync"),
            (4, 2, "4. Role verified (PREMIUM)", "ret"),
            (2, 3, "5. render_pdf_with_qr(audit_data)", "sync"),
            (3, 3, "6. Generate UUID sertifikat & QR Code image", "self"),
            (3, 2, "7. PDF stream buffer", "ret"),
            (2, 1, "8. 200 OK (application/pdf, Content-Disposition)", "ret"),
            (1, 0, "9. Unduh file 'Laporan_VeriText_[UUID].pdf'", "ret"),
            (0, 1, "10. [Alt] Pindai QR Code di kamera ponsel", "sync"),
            (1, 2, "11. GET /api/v1/reports/verify/{certificate_uuid}", "sync"),
            (2, 4, "12. SELECT * FROM audit_reports WHERE certificate_uuid", "sync"),
            (4, 2, "13. Data keaslian sertifikat", "ret"),
            (2, 1, "14. 200 OK (PublicVerificationPayload)", "ret"),
            (1, 0, "15. Tampilkan halaman verifikasi sah", "ret")
        ]
    },
    {
        "id": "SD9",
        "title": "Sequence Diagram: Kelola dan Hapus Riwayat Naskah",
        "filename": "SD9-Kelola dan Hapus Riwayat Naskah",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":HistoryView\n(Vue 3)"),
            ("api", ":DocumentAPI\n(FastAPI)"),
            ("srv", ":DocumentService"),
            ("storage", ":FileStorageEngine"),
            ("db", ":PostgreSQL (Cascade)")
        ],
        "messages": [
            (0, 1, "1. Klik 'Hapus Permanen' pada kartu naskah", "sync"),
            (1, 0, "2. Modal konfirmasi: 'Aksi ini ireversibel'", "ret"),
            (0, 1, "3. Konfirmasi tombol 'Ya, Hapus Permanen'", "sync"),
            (1, 2, "4. DELETE /api/v1/documents/{id} (Bearer JWT)", "sync"),
            (2, 3, "5. hard_delete_document(doc_id, user_id)", "sync"),
            (3, 4, "6. unlink(physical_file_path)", "sync"),
            (4, 3, "7. Berkas fisik terhapus dari disk", "ret"),
            (3, 5, "8. DELETE FROM documents WHERE id (Cascade to audit, chat)", "sync"),
            (5, 3, "9. Cascade deleted: tasks, sentences, chat", "ret"),
            (3, 5, "10. INSERT INTO audit_logs (event='DOCUMENT_HARD_DELETED')", "sync"),
            (5, 3, "11. Audit log recorded (UU PDP Compliance)", "ret"),
            (3, 2, "12. Deletion completed successfully", "ret"),
            (2, 1, "13. 200 OK (message='Document permanently deleted')", "ret"),
            (1, 0, "14. Hapus kartu dokumen dari daftar riwayat", "ret")
        ]
    },
    {
        "id": "SD10",
        "title": "Sequence Diagram: Beli Kuota Token dan Upgrade Premium",
        "filename": "SD10-Beli Kuota Token dan Upgrade Premium",
        "participants": [
            ("user", "User:Pengguna"),
            ("view", ":BillingView"),
            ("api", ":BillingAPI"),
            ("midtrans", ":MidtransSnapAPI"),
            ("db", ":PostgreSQL")
        ],
        "messages": [
            (0, 1, "1. Pilih skema: By Token (25 token) atau Paket Pro", "sync"),
            (1, 2, "2. POST /api/v1/billing/checkout (scheme, amount)", "sync"),
            (2, 4, "3. INSERT INTO invoices (status='PENDING')", "sync"),
            (4, 2, "4. Invoice created (order_id)", "ret"),
            (2, 3, "5. create_snap_transaction(order_id, gross_amount)", "sync"),
            (3, 2, "6. SnapToken & RedirectUrl", "ret"),
            (2, 1, "7. 200 OK (snap_token)", "ret"),
            (1, 0, "8. Buka popup modal Midtrans Snap", "ret"),
            (0, 3, "9. Pengguna membayar via QRIS / VA", "sync"),
            (3, 2, "10. POST /api/v1/billing/webhook (Midtrans Notification)", "sync"),
            (2, 2, "11. Verifikasi SHA-512 signature hash", "self"),
            (2, 4, "12. UPDATE invoices SET status='SETTLEMENT'", "sync"),
            (2, 4, "13. UPDATE token_wallets SET balance += 25", "sync"),
            (2, 4, "14. UPDATE users SET role='PREMIUM'", "sync"),
            (4, 2, "15. Transaksi committed atomik", "ret"),
            (2, 3, "16. 200 OK (Webhook Handled)", "ret"),
            (1, 2, "17. Smart polling: GET /api/v1/billing/orders/{id}", "sync"),
            (2, 1, "18. 200 OK (status='SETTLEMENT', role='PREMIUM')", "ret"),
            (1, 0, "19. Notifikasi 'Akun Anda kini PREMIUM! Saldo: 25 Token'", "ret")
        ]
    },
    {
        "id": "SD11",
        "title": "Sequence Diagram: Pantau Dasbor Analitik dan Log Transaksi",
        "filename": "SD11-Pantau Dasbor Analitik dan Log Transaksi",
        "participants": [
            ("admin", "Admin:Admin\n(Read-Only)"),
            ("view", ":AdminDashboard\n(Vue 3)"),
            ("api", ":AdminAPI\n(FastAPI)"),
            ("db", ":PostgreSQL\n(SELECT Only)"),
            ("worker", ":CeleryTelemetry\n(Redis Inspect)")
        ],
        "messages": [
            (0, 1, "1. Buka Halaman Dasbor Admin", "sync"),
            (1, 2, "2. GET /api/v1/admin/analytics (Bearer JWT)", "sync"),
            (2, 2, "3. Verifikasi role == 'ADMIN' (Read-Only Guard)", "self"),
            (2, 3, "4. SELECT COUNT(*), AVG(scores) FROM audit_tasks", "sync"),
            (3, 2, "5. Data statistik audit naskah", "ret"),
            (2, 3, "6. SELECT SUM(gross_amount) FROM invoices WHERE status='SETTLEMENT'", "sync"),
            (3, 2, "7. Data total pendapatan (Revenue)", "ret"),
            (2, 4, "8. inspect().active(), inspect().reserved()", "sync"),
            (4, 2, "9. Telemetri beban antrean worker Celery", "ret"),
            (2, 1, "10. 200 OK (AnalyticsDashboardPayload)", "ret"),
            (1, 0, "11. Render grafik tren pemindaian & kartu metrik", "ret"),
            (0, 1, "12. Buka Tab 'Log Transaksi Midtrans'", "sync"),
            (1, 2, "13. GET /api/v1/admin/transactions (page, limit)", "sync"),
            (2, 3, "14. SELECT * FROM invoices ORDER BY created_at DESC", "sync"),
            (3, 2, "15. Daftar 50 transaksi terbaru", "ret"),
            (2, 1, "16. 200 OK (InvoicesListPayload)", "ret"),
            (1, 0, "17. Tampilkan tabel transaksi (Murni Read-Only)", "ret")
        ]
    }
]

def render_sd(def_item):
    name = def_item["filename"]
    participants = def_item["participants"]
    msgs = def_item["messages"]
    p_count = len(participants)

    width = 1320
    top_y = 40
    msg_step = 50
    bottom_y = top_y + 80 + len(msgs) * msg_step + 40
    dw_h = bottom_y + 40

    dw = DrawioWriter(f"sd_{def_item['id'].lower()}", def_item["title"], width=width, height=dw_h)
    canvas = PngCanvas(width=width, height=dw_h, scale=2)

    spacing = (width - 200) / max(1, (p_count - 1))
    start_x = 100

    p_positions = []
    for i, (pid, plabel) in enumerate(participants):
        px = start_x + i * spacing
        p_positions.append(px)
        
        # Participant Box (Strictly B&W)
        canvas.draw_box(px - 70, top_y, 140, 46, plabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=4, font_size=9.5, bold=True)
        dw.add_node(f"part_{pid}", plabel, px - 70, top_y, 140, 46,
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;fontStyle=1;align=center;")
        
        # Lifeline (dashed line straight down)
        canvas.draw_arrow(px, top_y + 46, px, bottom_y, dashed=True, color="#000000", stroke_width=1.2)
        dw.add_edge(f"line_{pid}", source_point=(px, top_y + 46), target_point=(px, bottom_y), value="", style="dashed=1;strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # Messages
    for idx, (src_idx, tgt_idx, m_text, m_type) in enumerate(msgs):
        cur_y = top_y + 70 + idx * msg_step
        x1 = p_positions[src_idx]
        x2 = p_positions[tgt_idx]

        is_self = (src_idx == tgt_idx)
        is_ret = (m_type == "ret")

        if is_self:
            # Self call loop to right
            canvas.draw_polyline_arrow([(x1, cur_y - 8), (x1 + 35, cur_y - 8), (x1 + 35, cur_y + 12), (x1, cur_y + 12)], label=m_text, color="#000000", stroke_width=1.2)
            dw.add_edge(f"sd_msg_{idx}", value=m_text, style="edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;",
                        source_point=(x1, cur_y - 8), target_point=(x1, cur_y + 12),
                        waypoints=[(x1 + 35, cur_y - 8), (x1 + 35, cur_y + 12)])
        else:
            if is_ret:
                canvas.draw_arrow(x1, cur_y, x2, cur_y, label=m_text, color="#000000", stroke_width=1.2, dashed=True)
                dw.add_edge(f"sd_msg_{idx}", value=m_text, style="dashed=1;strokeColor=#000000;strokeWidth=1.2;endArrow=open;",
                            source_point=(x1, cur_y), target_point=(x2, cur_y))
            else:
                canvas.draw_arrow(x1, cur_y, x2, cur_y, label=m_text, color="#000000", stroke_width=1.5, dashed=False)
                dw.add_edge(f"sd_msg_{idx}", value=m_text, style="strokeColor=#000000;strokeWidth=1.5;endArrow=block;",
                            source_point=(x1, cur_y), target_point=(x2, cur_y))

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")

def main():
    for item in SD_DATA:
        render_sd(item)

if __name__ == "__main__":
    main()
