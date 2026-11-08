import os
from diagram_builder import DrawioWriter, PngCanvas

DRAWIO_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/drawio"
EXPORT_DIR = "/Users/azrlb23/Documents/IPPL/diagrams/exported"

def generate_use_case_diagram():
    name = "Use Case Diagram"
    dw = DrawioWriter("uc-diagram", "Use Case Diagram VeriText AI", width=1280, height=790)
    canvas = PngCanvas(width=1280, height=790, scale=2)

    # System boundary box (Pure Black & White, No Top-Left Title/Header Box)
    canvas.draw_box(270, 40, 720, 710, "", fill="#FFFFFF", stroke="#000000", stroke_width=2, radius=0)
    canvas.draw_text(630, 58, "Boundary Sistem: VeriText AI Platform", font_size=12, bold=True, fill="#000000")

    dw.add_node("sys_bound", "Boundary Sistem: VeriText AI Platform", 270, 40, 720, 710,
                "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;align=center;verticalAlign=top;fontStyle=1;fontSize=12;fontColor=#000000;spacingTop=12;")

    # Stickman Actors (Standard UML)
    canvas.draw_stickman(50, 190, 160, 130, "Free User\n(Pengguna Gratis)")
    canvas.draw_stickman(50, 500, 160, 130, "Premium User\n(Pengguna Berbayar)")
    canvas.draw_stickman(1040, 350, 170, 130, "Admin (Read-Only)\n(Pengawas Sistem)")

    dw.add_node("act_free", "Free User\n(Pengguna Gratis)", 90, 195, 80, 105,
                "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;")
    dw.add_node("act_prem", "Premium User\n(Pengguna Berbayar)", 90, 505, 80, 105,
                "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;")
    dw.add_node("act_admin", "Admin (Read-Only)\n(Pengawas Sistem)", 1085, 355, 80, 105,
                "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;")

    use_cases = [
        # Left column inside boundary
        ("UC-01", "UC-01: Masuk dan\nRegistrasi Akun", 310, 90, 240, 52),
        ("UC-02", "UC-02: Kelola Profil\ndan Kata Sandi", 310, 170, 240, 52),
        ("UC-03", "UC-03: Unggah dan\nValidasi Naskah", 310, 250, 240, 52),
        ("UC-05", "UC-05: Tinjau Laporan dan\nHeatmap Kemiripan", 310, 350, 240, 52),
        ("UC-09", "UC-09: Kelola dan Hapus\nRiwayat Naskah (PDP)", 310, 450, 240, 52),
        ("UC-10", "UC-10: Beli Kuota Token\ndan Upgrade Premium", 310, 560, 240, 52),
        ("UC-08", "UC-08: Unduh Laporan PDF\ndan Verifikasi QR", 310, 670, 240, 52),
        # Right column inside boundary
        ("UC-04", "UC-04: Deteksi Plagiarisme\nHybrid 3-Tahap", 690, 250, 250, 52),
        ("UC-06", "UC-06: Konsultasi Naskah\nvia AI Chatbot", 690, 350, 250, 52),
        ("UC-07", "UC-07: Parafrase Instan dan\nCek Ulang Kalimat", 690, 440, 250, 52),
        ("UC-11", "UC-11: Pantau Dasbor Analitik\ndan Log Transaksi", 690, 600, 250, 58),
    ]

    for ucid, uclabel, x, y, w, h in use_cases:
        canvas.draw_ellipse(x, y, w, h, uclabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, font_size=10)
        dw.add_node(ucid.replace("-", "_").lower(), uclabel, x, y, w, h,
                    "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;fontStyle=1;align=center;")

    # Draw non-crossing radiating associations from Free User
    free_ucs = ["UC-01", "UC-02", "UC-03", "UC-05", "UC-09", "UC-10"]
    for ucid in free_ucs:
        uc = [u for u in use_cases if u[0] == ucid][0]
        canvas.draw_arrow(200, 255, uc[2], uc[3] + uc[5]/2, color="#000000", stroke_width=1.2)
        dw.add_edge(f"edge_free_{ucid}", "act_free", ucid.replace("-", "_").lower(), style="strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # Premium User Generalization to Free User (UML Standard: inherits all base user capabilities)
    canvas.draw_arrow(130, 495, 130, 335, color="#000000", stroke_width=1.5)
    dw.add_edge("gen_prem_free", "act_prem", "act_free", style="edgeStyle=orthogonalEdgeStyle;endArrow=block;endFill=0;strokeColor=#000000;strokeWidth=1.5;")

    # Direct associations for Premium-enhanced features (clean, non-crossing)
    prem_direct_ucs = ["UC-10", "UC-08"]
    for ucid in prem_direct_ucs:
        uc = [u for u in use_cases if u[0] == ucid][0]
        canvas.draw_arrow(200, 585, uc[2], uc[3] + uc[5]/2, color="#000000", stroke_width=1.2)
        dw.add_edge(f"edge_prem_{ucid}", "act_prem", ucid.replace("-", "_").lower(), style="strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # Include & Extend relations
    # UC-03 includes UC-04
    canvas.draw_arrow(550, 276, 690, 276, "<<include>>", color="#000000", stroke_width=1.2, dashed=True)
    dw.add_edge("inc_03_04", "uc_03", "uc_04", "<<include>>", "dashed=1;strokeColor=#000000;strokeWidth=1.2;endArrow=open;")

    # UC-06 & UC-07 extend UC-05
    canvas.draw_arrow(690, 376, 550, 376, "<<extend>>", color="#000000", stroke_width=1.2, dashed=True)
    dw.add_edge("ext_06_05", "uc_06", "uc_05", "<<extend>>", "dashed=1;strokeColor=#000000;strokeWidth=1.2;endArrow=open;")

    canvas.draw_arrow(690, 455, 545, 390, "<<extend>>", color="#000000", stroke_width=1.2, dashed=True)
    dw.add_edge("ext_07_05", "uc_07", "uc_05", "<<extend>>", "dashed=1;strokeColor=#000000;strokeWidth=1.2;endArrow=open;")

    # Admin associations (UC-01 and UC-11)
    canvas.draw_arrow(1040, 420, 940, 629, color="#000000", stroke_width=1.2)
    dw.add_edge("edge_admin_11", "act_admin", "uc_11", style="strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    canvas.draw_polyline_arrow([(1040, 390), (980, 116), (550, 116)], color="#000000", stroke_width=1.2)
    dw.add_edge("edge_admin_01", "act_admin", "uc_01", style="edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_architecture_diagram():
    name = "Architecture Diagram"
    dw = DrawioWriter("arch-diagram", "Architecture Diagram VeriText AI", width=1360, height=980)
    canvas = PngCanvas(width=1360, height=980, scale=2)

    layers = [
        ("Layer 1: Lapisan Presentasi (Frontend Web Client)", 40, 190, [
            ("Vue 3.5 SPA", "Vue 3.5 Composition API + TypeScript 5.7\nReactivity Core & Views"),
            ("Vite 6 & Pinia 2.3", "Vite 6 Bundler & DevServer\nPinia 2.3 Modular State Management"),
            ("Tailwind CSS 3.4", "Academic Utility-First Styling\nSplit-Screen Workspace Layout"),
            ("Axios 1.7 HTTP Client", "JWT Bearer Interceptor, Error Handler\n& Smart Polling Manager")
        ]),
        ("Layer 2: Lapisan Logika Bisnis & Gateway API (Backend Core)", 270, 190, [
            ("FastAPI 0.115 Framework", "High-Performance ASGI Framework\nPydantic v2 Request/Response Schemas"),
            ("Auth & Security Guard", "JWT Access/Refresh Tokens, Google OAuth 2.0\nPassword Bcrypt Hashing & Rate Limiting"),
            ("Audit Orchestrator", "Task Dispatcher, Token Cost Calculator\n& In-Place Paraphrase Manager"),
            ("Billing & Webhook Service", "Midtrans Snap Integration & SHA-512\nWebhook Instant Role Upgrade (PREMIUM)")
        ]),
        ("Layer 3: Lapisan Komputasi Asinkron & AI Pipeline (Celery Worker & ML Engine)", 500, 200, [
            ("Step 1: Winnowing Lexical", "Rabin-Karp Rolling Hash (k=5, w=4)\nExact Verbatim Match (Red Tier 1)"),
            ("Step 2: Semantic AI & HNSW", "paraphrase-multilingual-MiniLM-L12-v2 (384-d)\nLazarusNLP/all-indobert-base-v4 Re-Ranker"),
            ("Step 3: Stylometric & AI Judge", "Burstiness B & Type-Token Ratio (TTR)\nGemini 2.5 Flash / OpenRouter Fallback"),
            ("Celery Worker Cluster", "Redis 7.2 Message Broker & Result Backend\nPriority Queue untuk Pengguna PREMIUM")
        ]),
        ("Layer 4: Lapisan Persistensi Data, Korpus Otomatis & Layanan Eksternal", 740, 200, [
            ("PostgreSQL 16 + pgvector", "13 Relational Tables & HNSW Vector Index\nCosine Distance (<=>) Operator"),
            ("Automated Corpus Harvesters", "Dual-Scope Academic Graph APIs:\nOpenAlex, DOAJ, Semantic Scholar, Crossref"),
            ("Google Grounding / Web Scanner", "Gemini Grounding & Campus Repository Search\nVerifikasi Tautan Publik Anti-Halusinasi"),
            ("Midtrans Payment Gateway", "Snap API, QRIS, Virtual Account, Credit Card\n& Webhook Settlement Auto-Activation")
        ])
    ]

    for title, y, h, modules in layers:
        canvas.draw_box(40, y, 1280, h, "", fill="#FFFFFF", stroke="#000000", stroke_width=2, radius=4)
        canvas.draw_text(60, y + 16, title, font_size=11, bold=True, fill="#000000", align="left")
        
        dw.add_node(f"layer_{y}", title, 40, y, 1280, h,
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;align=left;verticalAlign=top;fontStyle=1;fontSize=11.5;fontColor=#000000;spacingLeft=16;spacingTop=10;")

        mod_w = 285
        mod_gap = 16
        start_x = 65
        for idx, (m_title, m_desc) in enumerate(modules):
            mx = start_x + idx * (mod_w + mod_gap)
            my = y + 44
            mh = h - 60
            canvas.draw_box(mx, my, mod_w, mh, f"{m_title}\n\n{m_desc}", fill="#FFFFFF", stroke="#000000", stroke_width=1.2, radius=4, font_size=9.5)
            dw.add_node(f"mod_{y}_{idx}", f"{m_title}\n\n{m_desc}", mx, my, mod_w, mh,
                        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.2;fontColor=#000000;fontSize=9.5;align=center;")

    # Inter-layer Flow Connectors (B&W)
    canvas.draw_arrow(680, 230, 680, 270, "REST API JSON / Bearer JWT (HTTPS)", color="#000000", stroke_width=1.5)
    canvas.draw_arrow(680, 460, 680, 500, "Celery Task Queue via Redis Broker", color="#000000", stroke_width=1.5)
    canvas.draw_arrow(680, 700, 680, 740, "SQLAlchemy Async Engine & Vector Search", color="#000000", stroke_width=1.5)

    dw.add_edge("edge_l1_l2", "layer_40", "layer_270", "REST API JSON / Bearer JWT", "strokeColor=#000000;strokeWidth=1.5;endArrow=block;")
    dw.add_edge("edge_l2_l3", "layer_270", "layer_500", "Celery Task Queue via Redis Broker", "strokeColor=#000000;strokeWidth=1.5;endArrow=block;")
    dw.add_edge("edge_l3_l4", "layer_500", "layer_740", "SQLAlchemy Async & pgvector", "strokeColor=#000000;strokeWidth=1.5;endArrow=block;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_component_diagram():
    name = "Component Diagram"
    dw = DrawioWriter("comp-diagram", "Component Diagram VeriText AI", width=1350, height=880)
    canvas = PngCanvas(width=1350, height=880, scale=2)

    comps = [
        ("comp_fe", "<<component>>\nFrontend Web Client\n(Vue 3.5 + Vite + Pinia)", 50, 60, 240, 85),
        ("comp_auth", "<<component>>\nAuth & RBAC Service\n(OAuth & JWT Manager)", 350, 60, 240, 85),
        ("comp_prep", "<<component>>\nDocument Preprocessor\n(Parser & Word Counter)", 650, 60, 250, 85),
        ("comp_orch", "<<component>>\nHybrid Audit Orchestrator\n(3-Step Detection Pipeline)", 960, 60, 270, 85),

        ("comp_bill", "<<component>>\nBilling & Wallet Service\n(Midtrans Webhook & Token)", 50, 280, 250, 85),
        ("comp_rep", "<<component>>\nReport & Certificate Service\n(PDF Generator & QR Verifier)", 350, 280, 250, 85),
        ("comp_vec", "<<component>>\nSemantic Vector Engine\n(SBERT + IndoBERT + pgvector)", 650, 280, 260, 85),
        ("comp_chat", "<<component>>\nAcademic Assistant\n(AI Guardrail + Gemini Parafrase)", 960, 280, 270, 85),

        ("comp_adm", "<<component>>\nAdmin Telemetry Service\n(100% Read-Only Monitoring)", 350, 500, 260, 85),
        ("comp_db", "<<database>>\nPostgreSQL 16 & pgvector\n(13 SQL Relational Tables)", 650, 500, 270, 85),
        ("comp_ext", "<<external>>\nAcademic APIs & Midtrans\n(OpenAlex, DOAJ, Midtrans Snap)", 960, 500, 270, 85)
    ]

    for cid, label, x, y, w, h in comps:
        canvas.draw_box(x, y, w, h, label, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=4, font_size=10, bold=True)
        dw.add_node(cid, label, x, y, w, h,
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;fontStyle=1;align=center;")

    # Interfaces & Connections (Pure Black & White, Orthogonal obstacle-avoiding)
    canvas.draw_arrow(290, 102, 350, 102, "IAuthAPI", color="#000000", stroke_width=1.2)
    dw.add_edge("e_fe_auth", "comp_fe", "comp_auth", "IAuthAPI", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    canvas.draw_arrow(170, 145, 170, 280, "IBillingAPI", color="#000000", stroke_width=1.2)
    dw.add_edge("e_fe_bill", "comp_fe", "comp_bill", "IBillingAPI", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    canvas.draw_polyline_arrow([(240, 145), (240, 210), (475, 210), (475, 280)], "IReportAPI", color="#000000", stroke_width=1.2)
    dw.add_edge("e_fe_rep", "comp_fe", "comp_rep", "IReportAPI", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(240, 210), (475, 210)])

    canvas.draw_arrow(590, 102, 650, 102, "IDocValidation", color="#000000", stroke_width=1.2)
    dw.add_edge("e_auth_prep", "comp_auth", "comp_prep", "IDocValidation", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    canvas.draw_arrow(900, 102, 960, 102, "IPipelineDispatch", color="#000000", stroke_width=1.2)
    dw.add_edge("e_prep_orch", "comp_prep", "comp_orch", "IPipelineDispatch", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    canvas.draw_polyline_arrow([(1020, 145), (1020, 210), (780, 210), (780, 280)], "ISemanticSearch", color="#000000", stroke_width=1.2)
    dw.add_edge("e_orch_vec", "comp_orch", "comp_vec", "ISemanticSearch", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(1020, 210), (780, 210)])

    canvas.draw_arrow(1095, 145, 1095, 280, "IAssistantContext", color="#000000", stroke_width=1.2)
    dw.add_edge("e_orch_chat", "comp_orch", "comp_chat", "IAssistantContext", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Database connections
    canvas.draw_arrow(780, 365, 780, 500, "pgvector SQL", color="#000000", stroke_width=1.2)
    dw.add_edge("e_vec_db", "comp_vec", "comp_db", "pgvector SQL", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    canvas.draw_polyline_arrow([(990, 365), (990, 440), (880, 440), (880, 500)], "Audit Context", color="#000000", stroke_width=1.2)
    dw.add_edge("e_chat_db", "comp_chat", "comp_db", "Audit Context", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(990, 440), (880, 440)])

    canvas.draw_arrow(1095, 365, 1095, 500, "Gemini 2.5 API", color="#000000", stroke_width=1.2)
    dw.add_edge("e_chat_ext", "comp_chat", "comp_ext", "Gemini 2.5 API", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Clean orthogonal routing for Billing -> Database (corridor y=440 between row 2 and 3)
    canvas.draw_polyline_arrow([(175, 365), (175, 440), (650, 440), (650, 520)], "Transaction Ledger", color="#000000", stroke_width=1.2)
    dw.add_edge("e_bill_db", "comp_bill", "comp_db", "Transaction Ledger", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(175, 440), (650, 440)])

    canvas.draw_arrow(610, 542, 650, 542, "100% SELECT Only", color="#000000", stroke_width=1.2)
    dw.add_edge("e_adm_db", "comp_adm", "comp_db", "100% SELECT Only", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_class_diagram():
    name = "Class Diagram"
    dw = DrawioWriter("class-diagram", "Class Diagram VeriText AI", width=1400, height=980)
    canvas = PngCanvas(width=1400, height=980, scale=2)

    # 4-Row Logical Grid Layout to prevent ANY line from passing through classes:
    # Row 1 (y=40): Session (Col 0), User (Col 1), TokenWallet (Col 2), TokenTransaction (Col 3)
    # Row 2 (y=280): Document (Col 0), AuditTask (Col 1), AuditReport (Col 2), Invoice (Col 3)
    # Row 3 (y=510): AuditSentence (Col 0), ChatSession (Col 1), ChatMessage (Col 2), AuditLog (Col 3)
    # Row 4 (y=740): CorpusDocument (Col 1), DocumentChunk (Col 2)

    classes = [
        # Row 1
        ("Session", 50, 40, 270, 150, [
            ("+ id: UUID", "+ user_id: UUID", "+ refresh_token_hash: String", "+ ip_address: String", "+ expires_at: Timestamp"),
            ("+ create_session()", "+ revoke_session()", "+ is_valid(): Boolean")
        ]),
        ("User", 380, 40, 270, 210, [
            ("+ id: UUID", "+ email: String", "+ full_name: String", "+ role: UserRole (FREE/PREMIUM/ADMIN)", "+ password_hash: String", "+ is_active: Boolean", "+ created_at: Timestamp"),
            ("+ register()", "+ authenticate()", "+ update_profile()", "+ change_password()")
        ]),
        ("TokenWallet", 710, 40, 280, 190, [
            ("+ id: UUID", "+ user_id: UUID", "+ balance: Integer", "+ ai_trial_remaining: Integer = 3", "+ ai_chat_allowance_remaining: Integer = 0", "+ updated_at: Timestamp"),
            ("+ debit_tokens(amount)", "+ debit_ai_chat_credit()", "+ credit_tokens(amount)", "+ get_balance(): Integer")
        ]),
        ("TokenTransaction", 1050, 40, 280, 160, [
            ("+ id: UUID", "+ wallet_id: UUID", "+ amount: Integer", "+ transaction_type: TxType", "+ reference_id: String", "+ created_at: Timestamp"),
            ("+ record_transaction()", "+ get_history()")
        ]),

        # Row 2
        ("Document", 50, 280, 270, 180, [
            ("+ id: UUID", "+ user_id: UUID", "+ title: String", "+ file_path: String", "+ word_count: Integer", "+ file_size: Integer", "+ created_at: Timestamp"),
            ("+ upload_document()", "+ count_words(): Integer", "+ hard_delete()")
        ]),
        ("AuditTask", 380, 280, 270, 190, [
            ("+ id: UUID", "+ document_id: UUID", "+ status: TaskStatus", "+ lexical_score: Float", "+ semantic_score: Float", "+ stylometric_score: Float", "+ composite_score: Float", "+ execution_time_sec: Float"),
            ("+ dispatch_audit()", "+ calculate_composite()", "+ complete_audit()")
        ]),
        ("AuditReport", 710, 280, 280, 160, [
            ("+ id: UUID", "+ task_id: UUID", "+ certificate_uuid: UUID", "+ qr_code_url: String", "+ pdf_report_path: String", "+ generated_at: Timestamp"),
            ("+ generate_pdf_report()", "+ verify_certificate(): Boolean")
        ]),
        ("Invoice", 1050, 280, 280, 190, [
            ("+ id: UUID", "+ user_id: UUID", "+ order_id: String", "+ purchase_scheme: PurchaseScheme", "+ token_amount: Integer", "+ gross_amount: Decimal", "+ status: InvoiceStatus", "+ snap_token: String"),
            ("+ create_invoice()", "+ mark_settled()", "+ mark_expired()")
        ]),

        # Row 3
        ("AuditSentence", 50, 510, 270, 180, [
            ("+ id: UUID", "+ task_id: UUID", "+ sentence_text: Text", "+ sentence_order: Integer", "+ match_type: MatchType (RED/ORANGE/YELLOW)", "+ similarity_score: Float", "+ matched_source_id: UUID"),
            ("+ mark_highlight()", "+ update_in_place_text()")
        ]),
        ("ChatSession", 380, 510, 270, 160, [
            ("+ id: UUID", "+ user_id: UUID", "+ document_id: UUID", "+ title: String", "+ created_at: Timestamp"),
            ("+ start_session()", "+ hard_delete_session()")
        ]),
        ("ChatMessage", 710, 510, 280, 180, [
            ("+ id: UUID", "+ session_id: UUID", "+ role: MessageRole (USER/ASSISTANT)", "+ content: Text", "+ mode: ParaphraseMode", "+ suggested_options: JSONB", "+ applied_to_document: Boolean"),
            ("+ send_message()", "+ generate_3_options()", "+ apply_to_sentence()")
        ]),
        ("AuditLog", 1050, 510, 280, 160, [
            ("+ id: UUID", "+ actor_id: UUID", "+ event_type: String", "+ ip_address: String", "+ description: Text", "+ created_at: Timestamp"),
            ("+ log_event()", "+ get_admin_logs()")
        ]),

        # Row 4
        ("CorpusDocument", 380, 740, 270, 180, [
            ("+ id: UUID", "+ source_name: String", "+ doi_or_url: String", "+ title: String", "+ author: String", "+ year: Integer", "+ language: String"),
            ("+ harvest_from_api()", "+ extract_chunks()")
        ]),
        ("DocumentChunk", 710, 740, 280, 170, [
            ("+ id: UUID", "+ corpus_doc_id: UUID", "+ chunk_text: Text", "+ embedding: vector(384)", "+ kgram_hashes: BigInt[]"),
            ("+ compute_embedding()", "+ search_knn_hnsw()")
        ])
    ]

    for cname, x, y, w, h, (attrs, methods) in classes:
        # Title box
        canvas.draw_box(x, y, w, 28, cname, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=10, bold=True)
        # Attributes box
        attr_h = len(attrs) * 15 + 10
        canvas.draw_box(x, y + 28, w, attr_h, "\n".join(attrs), fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=8.5, align="left")
        # Methods box
        meth_h = len(methods) * 15 + 10
        canvas.draw_box(x, y + 28 + attr_h, w, meth_h, "\n".join(methods), fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=8.5, align="left")

        dw_val = f"{cname}\n---\n" + "\n".join(attrs) + "\n---\n" + "\n".join(methods)
        dw.add_node(f"cls_{cname.lower()}", dw_val, x, y, w, h,
                    "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=28;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;")

    # Non-colliding Associations (Direct adjacent or clear horizontal corridors)
    # 1. User -> Session (Row 1 Col 1 -> Row 1 Col 0)
    canvas.draw_arrow(380, 110, 320, 110, "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_user_session", "cls_user", "cls_session", "1..*", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 2. User -> TokenWallet (Row 1 Col 1 -> Row 1 Col 2)
    canvas.draw_arrow(650, 110, 710, 110, "1..1", color="#000000", stroke_width=1.2)
    dw.add_edge("c_user_wallet", "cls_user", "cls_tokenwallet", "1..1", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 3. TokenWallet -> TokenTransaction (Row 1 Col 2 -> Row 1 Col 3)
    canvas.draw_arrow(990, 110, 1050, 110, "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_wallet_tx", "cls_tokenwallet", "cls_tokentransaction", "1..*", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 4. User -> Document (Corridor y=255)
    canvas.draw_polyline_arrow([(420, 250), (420, 255), (185, 255), (185, 280)], "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_user_doc", "cls_user", "cls_document", "1..*", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=none;", waypoints=[(420, 255), (185, 255)])

    # 5. TokenWallet -> Invoice (Corridor y=255)
    canvas.draw_polyline_arrow([(850, 230), (850, 255), (1190, 255), (1190, 280)], "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_wallet_inv", "cls_tokenwallet", "cls_invoice", "1..*", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=none;", waypoints=[(850, 255), (1190, 255)])

    # 6. Document -> AuditTask (Row 2 Col 0 -> Row 2 Col 1)
    canvas.draw_arrow(320, 360, 380, 360, "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_doc_task", "cls_document", "cls_audittask", "1..*", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 7. AuditTask -> AuditReport (Row 2 Col 1 -> Row 2 Col 2)
    canvas.draw_arrow(650, 360, 710, 360, "1..1", color="#000000", stroke_width=1.2)
    dw.add_edge("c_task_rep", "cls_audittask", "cls_auditreport", "1..1", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 8. AuditTask -> AuditSentence (Corridor y=495)
    canvas.draw_polyline_arrow([(420, 470), (420, 495), (185, 495), (185, 510)], "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_task_sent", "cls_audittask", "cls_auditsentence", "1..*", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=none;", waypoints=[(420, 495), (185, 495)])

    # 9. Document -> ChatSession (Corridor y=495)
    canvas.draw_polyline_arrow([(240, 460), (240, 495), (515, 495), (515, 510)], "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_doc_chat", "cls_document", "cls_chatsession", "1..*", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=none;", waypoints=[(240, 495), (515, 495)])

    # 10. ChatSession -> ChatMessage (Row 3 Col 1 -> Row 3 Col 2)
    canvas.draw_arrow(650, 590, 710, 590, "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_chat_msg", "cls_chatsession", "cls_chatmessage", "1..*", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    # 11. CorpusDocument -> DocumentChunk (Row 4 Col 1 -> Row 4 Col 2)
    canvas.draw_arrow(650, 810, 710, 810, "1..*", color="#000000", stroke_width=1.2)
    dw.add_edge("c_corp_chunk", "cls_corpusdocument", "cls_documentchunk", "1..*", "strokeColor=#000000;strokeWidth=1.2;endArrow=none;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_dfd0():
    name = "DFD0-Context Diagram"
    dw = DrawioWriter("dfd0-diagram", "DFD Level 0 Context Diagram VeriText AI", width=1280, height=880)
    canvas = PngCanvas(width=1280, height=880, scale=2)

    # Process 0 (Center Ellipse)
    canvas.draw_ellipse(480, 320, 320, 180, "0\nSistem Deteksi\nPlagiarisme Cerdas\nVeriText AI", fill="#FFFFFF", stroke="#000000", stroke_width=2, font_size=12)
    dw.add_node("p0", "0\nSistem Deteksi Plagiarisme Cerdas\nVeriText AI", 480, 320, 320, 180,
                "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;fontColor=#000000;fontSize=13;fontStyle=1;align=center;")

    entities = [
        ("ent_free", "Free User\n(Pengguna Gratis)", 60, 120, 190, 70),
        ("ent_prem", "Premium User\n(Pengguna Berbayar)", 60, 370, 190, 70),
        ("ent_admin", "Admin (Read-Only)\n(Pengawas Sistem)", 60, 620, 190, 70),

        ("ent_midtrans", "Midtrans Payment\nGateway", 1030, 120, 190, 70),
        ("ent_apis", "Dual-Scope Academic APIs\n(OpenAlex, DOAJ, Crossref)", 1030, 370, 190, 70),
        ("ent_ai", "Google Gemini 2.5 API\n& Search Grounding", 1030, 620, 190, 70)
    ]

    for eid, elabel, x, y, w, h in entities:
        canvas.draw_box(x, y, w, h, elabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=10.5, bold=True)
        dw.add_node(eid, elabel, x, y, w, h,
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=11;fontStyle=1;align=center;")

    # Inflows / Outflows with clean spacing to prevent crossing labels
    # Free User
    canvas.draw_arrow(250, 140, 490, 330, "Naskah Teks (<=2.500 kata), Login, Chat Trial", color="#000000")
    canvas.draw_arrow(490, 360, 250, 175, "Interactive Heatmap (Web View), Kuota", color="#000000")

    # Premium User
    canvas.draw_arrow(250, 390, 480, 400, "Naskah Panjang (Cap 5 Token), Order Token", color="#000000")
    canvas.draw_arrow(480, 430, 250, 425, "Laporan PDF Ber-QR, 3 Opsi Parafrase", color="#000000")

    # Admin
    canvas.draw_arrow(250, 635, 500, 485, "Permintaan Telemetri & Log Audit (GET)", color="#000000")
    canvas.draw_arrow(520, 495, 250, 665, "Dasbor Analitik, Log Transaksi & Health Status", color="#000000")

    # Midtrans
    canvas.draw_arrow(780, 340, 1030, 140, "Request Snap Token & Parameter Order", color="#000000")
    canvas.draw_arrow(1030, 175, 790, 365, "Webhook Settlement & Status Transaksi", color="#000000")

    # Academic APIs
    canvas.draw_arrow(800, 390, 1030, 390, "Kueri Metadata, DOI, Abstrak Jurnal", color="#000000")
    canvas.draw_arrow(1030, 425, 800, 425, "Dataset Korpus Nasional & Internasional", color="#000000")

    # AI / Search Grounding
    canvas.draw_arrow(780, 460, 1030, 635, "Prompt Kalimat Anomali & Konteks Naskah", color="#000000")
    canvas.draw_arrow(1030, 665, 760, 485, "Evaluasi AI Judge, Grounding Web & Saran", color="#000000")

    dw.add_edge("dfd0_e1", "ent_free", "p0", "Naskah, Login, Chat Trial", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e2", "p0", "ent_free", "Heatmap Web View, Status Kuota", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e3", "ent_prem", "p0", "Naskah Skripsi, Order Token, Parafrase", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e4", "p0", "ent_prem", "Laporan PDF QR, Invoice, 3 Opsi Parafrase", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e5", "ent_admin", "p0", "Permintaan Telemetri (GET)", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e6", "p0", "ent_admin", "Dasbor Analitik, Log Transaksi", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e7", "p0", "ent_midtrans", "Request Snap Token", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e8", "ent_midtrans", "p0", "Webhook Settlement Notification", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e9", "p0", "ent_apis", "Kueri Metadata & Abstrak", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e10", "ent_apis", "p0", "Data Publikasi Ilmiah", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e11", "p0", "ent_ai", "Prompt Evaluasi & Parafrase", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("dfd0_e12", "ent_ai", "p0", "Grounding Web & Respon Parafrase", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_dfd1():
    name = "DFD1-System Overview"
    dw = DrawioWriter("dfd1-diagram", "DFD Level 1 System Overview VeriText AI", width=1380, height=780)
    canvas = PngCanvas(width=1380, height=780, scale=2)

    processes = [
        ("p1", "1.0\nAutentikasi & Akun", 60, 80, 160, 75),
        ("p2", "2.0\nUnggah & Validasi", 360, 80, 170, 75),
        ("p3", "3.0\nDeteksi Hybrid 3-Tahap", 670, 80, 190, 75),
        ("p4", "4.0\nAI Chatbot & Parafrase", 990, 80, 190, 75),
        ("p6", "6.0\nToken & Midtrans Billing", 200, 360, 190, 75),
        ("p5", "5.0\nPelaporan & QR PDF", 580, 360, 190, 75),
        ("p7", "7.0\nMonitoring Layanan (Admin)", 960, 360, 200, 75),
    ]

    for pid, plabel, x, y, w, h in processes:
        canvas.draw_box(x, y, w, h, plabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=30, font_size=10, bold=True)
        dw.add_node(pid, plabel, x, y, w, h,
                    "rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10.5;fontStyle=1;align=center;")

    # Non-overlapping data stores (Zero horizontal collision)
    data_stores = [
        ("ds1", "D1: Users & TokenWallets", 60, 230, 220, 45),
        ("ds2", "D2: Documents & AuditTasks", 360, 230, 230, 45),
        ("ds3", "D3: Corpus & Vector Embeddings", 670, 230, 240, 45),
        ("ds5", "D5: ChatSessions & Messages", 990, 230, 240, 45),
        ("ds6", "D6: Invoices & Transactions", 200, 520, 230, 45),
        ("ds4", "D4: AuditReports & Certificates", 580, 520, 240, 45)
    ]

    for did, dlabel, x, y, w, h in data_stores:
        canvas.draw_box(x, y, w, h, dlabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=9.5, bold=True)
        dw.add_node(did, dlabel, x, y, w, h,
                    "html=1;dashed=0;whiteSpace=wrap;shape=partialRectangle;right=0;left=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=9.5;fontStyle=1;align=center;")

    # Connectors
    # Process 1.0 -> D1
    canvas.draw_arrow(140, 155, 170, 230, "Simpan User & Wallet", color="#000000")
    dw.add_edge("e_p1_d1", "p1", "ds1", "Simpan Akun & Saldo", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 2.0 -> D2
    canvas.draw_arrow(445, 155, 475, 230, "Simpan Metadata Naskah", color="#000000")
    dw.add_edge("e_p2_d2", "p2", "ds2", "Simpan Naskah", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 3.0 -> D2 & D3
    canvas.draw_arrow(730, 155, 550, 230, "Update Skor & Status Task", color="#000000")
    canvas.draw_arrow(790, 230, 765, 155, "Kueri Indeks Vektor HNSW", color="#000000")
    dw.add_edge("e_p3_d2", "p3", "ds2", "Update Skor", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_d3_p3", "ds3", "p3", "Vektor Korpus", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 4.0 -> D5
    canvas.draw_arrow(1085, 155, 1110, 230, "Riwayat Chat & Parafrase", color="#000000")
    dw.add_edge("e_p4_d5", "p4", "ds5", "Riwayat Percakapan", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 5.0: reads from D2, writes to D4
    canvas.draw_arrow(475, 275, 620, 360, "Ambil Data Audit & Skor", color="#000000")
    canvas.draw_arrow(675, 435, 700, 520, "Simpan Sertifikat & URL QR", color="#000000")
    dw.add_edge("e_d2_p5", "ds2", "p5", "Ambil Hasil Audit", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_p5_d4", "p5", "ds4", "Simpan Sertifikat", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 6.0 -> D6 & D1
    canvas.draw_arrow(295, 435, 315, 520, "Catat Invoice & Topup", color="#000000")
    canvas.draw_arrow(250, 360, 200, 275, "Auto-Upgrade Role -> PREMIUM", color="#000000")
    dw.add_edge("e_p6_d6", "p6", "ds6", "Catat Transaksi", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_p6_d1", "p6", "ds1", "Tambah Saldo Token", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Process 7.0 reads from D6 and D2
    canvas.draw_polyline_arrow([(960, 435), (960, 600), (350, 600), (350, 565)], "Baca Log Transaksi (GET)", color="#000000")
    dw.add_edge("e_p7_read", "p7", "ds6", "Agregasi Log Transaksi", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def generate_dfd2():
    name = "DFD2-Deteksi Plagiarisme Hybrid dan AI Chatbot"
    dw = DrawioWriter("dfd2-diagram", "DFD Level 2 Deteksi Plagiarisme Hybrid dan AI Chatbot", width=1380, height=520)
    canvas = PngCanvas(width=1380, height=520, scale=2)

    sub_processes = [
        ("p31", "3.1\nSegmentasi Kalimat &\nNormalisasi Teks", 50, 60, 190, 70),
        ("p32", "3.2 (Step 1)\nWinnowing Lexical\nFingerprinting", 310, 60, 200, 70),
        ("p33", "3.3 (Step 2)\nSBERT Multi-lingual\n& pgvector HNSW", 580, 60, 210, 70),
        ("p34", "3.4 (Step 3)\nStilometri & Gemini\nContextual AI Judge", 860, 60, 220, 70),
        ("p35", "3.5\nAgregasi Skor Komposit\n& Heatmap Multi-Warna", 1140, 60, 200, 70),

        ("p41", "4.1\nAcademic Guardrail &\nPrompt Validator", 310, 290, 210, 70),
        ("p42", "4.2\nGenerator 3 Opsi\nParafrase Kalimat/Paragraf", 580, 290, 220, 70),
        ("p43", "4.3\nTerapkan ke Naskah &\nHitung Ulang Skor In-Place", 860, 290, 220, 70)
    ]

    for spid, splabel, x, y, w, h in sub_processes:
        canvas.draw_box(x, y, w, h, splabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=25, font_size=9.5, bold=True)
        dw.add_node(spid, splabel, x, y, w, h,
                    "rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=9.5;fontStyle=1;align=center;")

    d_stores = [
        ("d_fingerprints", "D3.2: Rabin-Karp Hashes", 310, 175, 200, 40),
        ("d_chunks", "D3.1: Chunk Embeddings (384-d)", 580, 175, 210, 40),
        ("d_sentences", "D2.1: AuditSentences (Highlighted)", 860, 175, 220, 40)
    ]

    for did, dlabel, x, y, w, h in d_stores:
        canvas.draw_box(x, y, w, h, dlabel, fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=0, font_size=9, bold=True)
        dw.add_node(did, dlabel, x, y, w, h,
                    "html=1;dashed=0;whiteSpace=wrap;shape=partialRectangle;right=0;left=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=9;fontStyle=1;align=center;")

    # Sequential flow P3.1 -> P3.2 -> P3.3 -> P3.4 -> P3.5 (Plain Black)
    canvas.draw_arrow(240, 95, 310, 95, "Kalimat Bersih", color="#000000")
    canvas.draw_arrow(510, 95, 580, 95, "Skor Leksikal", color="#000000")
    canvas.draw_arrow(790, 95, 860, 95, "Skor Semantik", color="#000000")
    canvas.draw_arrow(1080, 95, 1140, 95, "Skor Stilometri", color="#000000")

    dw.add_edge("e_31_32", "p31", "p32", "Kalimat Bersih", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_32_33", "p32", "p33", "Leksikal Match", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_33_34", "p33", "p34", "Semantik Match", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_34_35", "p34", "p35", "Stilometri Match", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Stores accesses
    canvas.draw_arrow(410, 130, 410, 175, "Cek Hashes", color="#000000")
    canvas.draw_arrow(685, 130, 685, 175, "KNN Cosine (<=>)", color="#000000")
    canvas.draw_arrow(970, 130, 970, 175, "Simpan Tag Warna", color="#000000")

    dw.add_edge("e_32_fp", "p32", "d_fingerprints", "Hash Lookup", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_33_ch", "p33", "d_chunks", "KNN Cosine", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_34_sen", "p34", "d_sentences", "Tagging Warna", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")

    # Chatbot flow with clean orthogonal routing
    canvas.draw_polyline_arrow([(970, 215), (970, 255), (415, 255), (415, 290)], "Klik Kalimat Bermasalah", color="#000000")
    canvas.draw_arrow(520, 325, 580, 325, "Lolos Filter Akademik", color="#000000")
    canvas.draw_arrow(800, 325, 860, 325, "Pilih 1 dari 3 Variasi", color="#000000")
    canvas.draw_polyline_arrow([(970, 360), (970, 420), (1240, 420), (1240, 130)], "Update Teks & Hitung Ulang", color="#000000")

    dw.add_edge("e_sen_41", "d_sentences", "p41", "Klik Kalimat", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(970, 255), (415, 255)])
    dw.add_edge("e_41_42", "p41", "p42", "Konteks Valid", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_42_43", "p42", "p43", "Opsi Terpilih", "strokeColor=#000000;strokeWidth=1.2;endArrow=block;")
    dw.add_edge("e_43_35", "p43", "p35", "Update Teks & Hitung Ulang", "edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;strokeWidth=1.2;endArrow=block;", waypoints=[(970, 420), (1240, 420)])

    dw.save(f"{DRAWIO_DIR}/{name}.drawio")
    canvas.save(f"{EXPORT_DIR}/{name}.png")
    print(f"Generated {name}")


def main():
    generate_use_case_diagram()
    generate_architecture_diagram()
    generate_component_diagram()
    generate_class_diagram()
    generate_dfd0()
    generate_dfd1()
    generate_dfd2()

if __name__ == "__main__":
    main()
