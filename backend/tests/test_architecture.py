import os
import re
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


class TestVeriTextArchitecture(unittest.TestCase):
    def test_required_root_files_exist(self):
        required_files = [
            "docker-compose.yml",
            ".gitignore",
            ".env.example",
            "README.md",
        ]
        for f in required_files:
            path = os.path.join(ROOT_DIR, f)
            self.assertTrue(os.path.exists(path), f"Missing root file: {f}")

    def test_database_init_and_migrations_structure(self):
        db_dir = os.path.join(ROOT_DIR, "db")
        required_db_files = [
            os.path.join(db_dir, "init", "01_extensions.sql"),
            os.path.join(db_dir, "init", "02_schema_ddl.sql"),
            os.path.join(db_dir, "init", "03_seed_dml.sql"),
            os.path.join(db_dir, "migrations", "0001_initial_schema.sql"),
            os.path.join(db_dir, "migrations", "README.md"),
            os.path.join(db_dir, "README.md"),
        ]
        for f in required_db_files:
            self.assertTrue(os.path.exists(f), f"Missing database file: {f}")

    def test_docker_compose_configuration(self):
        dc_path = os.path.join(ROOT_DIR, "docker-compose.yml")
        with open(dc_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("pgvector/pgvector:pg16", content)
        self.assertIn("redis:7-alpine", content)
        self.assertIn("5432", content)
        self.assertIn("6379", content)
        self.assertIn("postgres_data", content)
        self.assertIn("redis_data", content)

    def test_all_14_database_models_defined(self):
        models_dir = os.path.join(BACKEND_DIR, "app", "models")
        expected_models = [
            "User",
            "Session",
            "PasswordReset",
            "TokenWallet",
            "TokenTransaction",
            "Invoice",
            "Document",
            "AuditTask",
            "AuditSentence",
            "AuditReport",
            "CorpusDocument",
            "DocumentChunk",
            "LexicalFingerprint",
            "AuditLog",
        ]

        init_file = os.path.join(models_dir, "__init__.py")
        with open(init_file, "r", encoding="utf-8") as f:
            init_content = f.read()

        for model in expected_models:
            self.assertIn(model, init_content, f"Model {model} is not exported in app/models/__init__.py")

    def test_alembic_initial_migration_covers_14_tables(self):
        migration_file = os.path.join(BACKEND_DIR, "alembic", "versions", "0001_initial_schema.py")
        self.assertTrue(os.path.exists(migration_file))

        with open(migration_file, "r", encoding="utf-8") as f:
            content = f.read()

        expected_tables = [
            "users",
            "sessions",
            "password_resets",
            "token_wallets",
            "token_transactions",
            "invoices",
            "documents",
            "audit_tasks",
            "audit_sentences",
            "audit_reports",
            "corpus_documents",
            "document_chunks",
            "lexical_fingerprints",
            "audit_logs",
        ]

        for tbl in expected_tables:
            self.assertIn(tbl, content, f"Table {tbl} not found in Alembic migration")

        # Verify pgvector extension and HNSW index
        self.assertIn("vector(384)", content)
        self.assertIn("hnsw", content)
        self.assertIn("pgcrypto", content)

    def test_api_v1_routers_mounted(self):
        router_file = os.path.join(BACKEND_DIR, "app", "api", "v1", "router.py")
        with open(router_file, "r", encoding="utf-8") as f:
            content = f.read()

        expected_subrouters = [
            "auth_router",
            "documents_router",
            "audits_router",
            "reports_router",
            "corpus_router",
            "billing_router",
            "admin_router",
        ]
        for sub in expected_subrouters:
            self.assertIn(sub, content, f"Sub-router {sub} not registered in api_v1_router")

    def test_frontend_structure_and_tier_colors(self):
        tailwind_config = os.path.join(FRONTEND_DIR, "tailwind.config.js")
        self.assertTrue(os.path.exists(tailwind_config))

        with open(tailwind_config, "r", encoding="utf-8") as f:
            content = f.read()

        # Semantic Tier Colors from SDD 3.6.2
        self.assertIn("#EF4444", content)  # Red Tier 1
        self.assertIn("#F97316", content)  # Orange Tier 2
        self.assertIn("#EAB308", content)  # Yellow Tier 3
        self.assertIn("#2563EB", content)  # Brand Blue

    def test_frontend_views_exist(self):
        views_dir = os.path.join(FRONTEND_DIR, "src", "views")
        expected_views = [
            "LandingView.vue",
            "DashboardView.vue",
            "AuditDetailView.vue",
            "LoginView.vue",
            "RegisterView.vue",
            "CorpusView.vue",
            "BillingView.vue",
            "VerifyView.vue",
        ]
        for v in expected_views:
            path = os.path.join(views_dir, v)
            self.assertTrue(os.path.exists(path), f"Frontend view {v} missing")

    def test_frontend_components_exist(self):
        comp_dir = os.path.join(FRONTEND_DIR, "src", "components")
        expected_components = [
            "Navbar.vue",
            "Footer.vue",
            "TierLegend.vue",
            "SimilarityGauge.vue",
            "HeatmapViewer.vue",
        ]
        for c in expected_components:
            path = os.path.join(comp_dir, c)
            self.assertTrue(os.path.exists(path), f"Frontend component {c} missing")


    def test_all_python_files_ast_syntax_validity(self):
        import ast
        for root, dirs, files in os.walk(BACKEND_DIR):
            dirs[:] = [d for d in dirs if d not in (".venv", "venv", "__pycache__", ".pytest_cache")]
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    with open(full_path, "r", encoding="utf-8") as py_file:
                        source = py_file.read()
                    try:
                        ast.parse(source, filename=full_path)
                    except SyntaxError as e:
                        self.fail(f"Syntax error in {full_path}: {e}")

    def test_frontend_json_and_tier_palette(self):
        import json
        for jf in ["package.json", "tsconfig.json", "tsconfig.node.json"]:
            path = os.path.join(FRONTEND_DIR, jf)
            self.assertTrue(os.path.exists(path), f"Missing frontend {jf}")
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)
                self.assertIsNotNone(content)

        # Check background colors in tailwind config
        tailwind_config = os.path.join(FRONTEND_DIR, "tailwind.config.js")
        with open(tailwind_config, "r", encoding="utf-8") as f:
            tw_content = f.read()
        self.assertIn("#FEF2F2", tw_content)
        self.assertIn("#FFF7ED", tw_content)
        self.assertIn("#FEFCE8", tw_content)


if __name__ == "__main__":
    unittest.main()
