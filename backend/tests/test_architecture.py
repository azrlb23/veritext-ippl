import ast
import json
import os
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


class TestVeriTextArchitecture(unittest.TestCase):
    def test_required_root_files_exist(self):
        for f in ["docker-compose.yml", ".gitignore", ".env.example", "README.md"]:
            self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, f)), f"Missing: {f}")

    def test_database_init_and_migrations_structure(self):
        db_dir = os.path.join(ROOT_DIR, "db")
        for f in [
            "init/01_extensions.sql", "init/02_schema_ddl.sql", "init/03_seed_dml.sql",
            "migrations/0001_initial_schema.sql", "migrations/README.md", "README.md",
        ]:
            self.assertTrue(os.path.exists(os.path.join(db_dir, f)), f"Missing db: {f}")

    def test_docker_compose_configuration(self):
        with open(os.path.join(ROOT_DIR, "docker-compose.yml"), "r", encoding="utf-8") as f:
            content = f.read()
        for s in ["pgvector/pgvector:pg16", "redis:7-alpine", "5432", "6379", "postgres_data", "redis_data"]:
            self.assertIn(s, content)

    def test_all_14_database_models_defined(self):
        with open(os.path.join(BACKEND_DIR, "app", "models", "__init__.py"), "r", encoding="utf-8") as f:
            content = f.read()
        for m in [
            "User", "Session", "PasswordReset", "TokenWallet", "TokenTransaction", "Invoice",
            "Document", "AuditTask", "AuditSentence", "AuditReport", "CorpusDocument",
            "DocumentChunk", "LexicalFingerprint", "AuditLog",
        ]:
            self.assertIn(m, content, f"Model {m} missing from __init__.py")

    def test_alembic_initial_migration_covers_14_tables(self):
        p = os.path.join(BACKEND_DIR, "alembic", "versions", "0001_initial_schema.py")
        self.assertTrue(os.path.exists(p))
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        for tbl in [
            "users", "sessions", "password_resets", "token_wallets", "token_transactions",
            "invoices", "documents", "audit_tasks", "audit_sentences", "audit_reports",
            "corpus_documents", "document_chunks", "lexical_fingerprints", "audit_logs",
        ]:
            self.assertIn(tbl, content, f"Table {tbl} not in 0001 migration")
        for extra in ["vector(384)", "hnsw", "pgcrypto"]:
            self.assertIn(extra, content)

    def test_alembic_0005_chat_and_subcredits_migration(self):
        p = os.path.join(BACKEND_DIR, "alembic", "versions", "0005_chat_and_subcredits.py")
        self.assertTrue(os.path.exists(p), "Missing 0005_chat_and_subcredits.py")
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        for s in ["0005_chat_and_subcredits", "0004_phase6_system_config", "chat_sessions", "chat_messages"]:
            self.assertIn(s, content, f"Expected {s} in 0005 migration")

    def test_api_v1_routers_mounted(self):
        with open(os.path.join(BACKEND_DIR, "app", "api", "v1", "router.py"), "r", encoding="utf-8") as f:
            content = f.read()
        for sub in [
            "auth_router", "documents_router", "audits_router",
            "reports_router", "billing_router", "admin_router",
        ]:
            self.assertIn(sub, content, f"Sub-router {sub} not mounted")

    def test_frontend_structure_and_tier_colors(self):
        with open(os.path.join(FRONTEND_DIR, "tailwind.config.js"), "r", encoding="utf-8") as f:
            content = f.read()
        for c in ["#EF4444", "#F97316", "#EAB308", "#2563EB"]:
            self.assertIn(c, content)

    def test_frontend_views_exist(self):
        views_dir = os.path.join(FRONTEND_DIR, "src", "views")
        for v in [
            "LandingView.vue", "RingkasanView.vue", "AuditDetailView.vue", "LoginView.vue",
            "RegisterView.vue", "AdminView.vue", "TokenView.vue", "VerifyView.vue", "RiwayatView.vue", "AkunView.vue", "AsistenView.vue",
        ]:
            self.assertTrue(os.path.exists(os.path.join(views_dir, v)), f"Missing view {v}")

    def test_frontend_components_exist(self):
        comp_dir = os.path.join(FRONTEND_DIR, "src", "components")
        for c in ["Navbar.vue", "Footer.vue", "TierLegend.vue", "HeatmapViewer.vue"]:
            self.assertTrue(os.path.exists(os.path.join(comp_dir, c)), f"Missing component {c}")

    def test_all_python_files_ast_syntax_validity(self):
        for root, dirs, files in os.walk(BACKEND_DIR):
            dirs[:] = [d for d in dirs if d not in (".venv", "venv", "__pycache__", ".pytest_cache")]
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    with open(full_path, "r", encoding="utf-8") as py_file:
                        ast.parse(py_file.read(), filename=full_path)

    def test_frontend_json_and_tier_palette(self):
        for jf in ["package.json", "tsconfig.json", "tsconfig.node.json"]:
            path = os.path.join(FRONTEND_DIR, jf)
            self.assertTrue(os.path.exists(path), f"Missing frontend {jf}")
            with open(path, "r", encoding="utf-8") as f:
                self.assertIsNotNone(json.load(f))
        with open(os.path.join(FRONTEND_DIR, "tailwind.config.js"), "r", encoding="utf-8") as f:
            tw_content = f.read()
        for bg in ["#FEF2F2", "#FFF7ED", "#FEFCE8"]:
            self.assertIn(bg, tw_content)


if __name__ == "__main__":
    unittest.main()
