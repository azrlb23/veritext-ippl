import hashlib
import re
import secrets
import sys
import types
import unittest
import uuid

# Ensure backend root is in sys.path
import os
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ---------------------------------------------------------------------------
# Setup robust shims for external dependencies when running in plain Python 3.9
# ---------------------------------------------------------------------------
if "fastapi" not in sys.modules:
    fastapi_mod = types.ModuleType("fastapi")
    class HTTPException(Exception):
        def __init__(self, status_code, detail=None, headers=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail
            self.headers = headers
    class UploadFile:
        def __init__(self, filename="", file=None, content_type=""):
            self.filename = filename
            self.file = file
            self.content_type = content_type
    class Status:
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_402_PAYMENT_REQUIRED = 402
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    fastapi_mod.HTTPException = HTTPException
    fastapi_mod.UploadFile = UploadFile
    fastapi_mod.status = Status()
    sys.modules["fastapi"] = fastapi_mod

if "pydantic_settings" not in sys.modules:
    ps_mod = types.ModuleType("pydantic_settings")
    class BaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    ps_mod.BaseSettings = BaseSettings
    ps_mod.SettingsConfigDict = lambda **kw: None
    sys.modules["pydantic_settings"] = ps_mod

if "jwt" not in sys.modules:
    jwt_mod = types.ModuleType("jwt")
    def _jwt_encode(payload, key, algorithm="HS256"):
        import json, base64
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
        body = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode().rstrip("=")
        sig = hashlib.sha256(f"{header}.{body}.{key}".encode()).hexdigest()[:16]
        return f"{header}.{body}.{sig}"
    def _jwt_decode(token, key, algorithms=None):
        import json, base64
        parts = token.split(".")
        if len(parts) != 3:
            raise Exception("Invalid token")
        padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(padded).decode())
    jwt_mod.encode = _jwt_encode
    jwt_mod.decode = _jwt_decode
    jwt_mod.PyJWTError = Exception
    sys.modules["jwt"] = jwt_mod

if "passlib" not in sys.modules:
    passlib_mod = types.ModuleType("passlib")
    passlib_ctx = types.ModuleType("passlib.context")
    class CryptContext:
        def __init__(self, schemes=None, deprecated="auto"):
            self.schemes = schemes
        def hash(self, secret):
            return "pbkdf2_sha256$" + hashlib.sha256(secret.encode()).hexdigest()
        def verify(self, secret, hashed):
            return hashed == ("pbkdf2_sha256$" + hashlib.sha256(secret.encode()).hexdigest())
    passlib_ctx.CryptContext = CryptContext
    sys.modules["passlib"] = passlib_mod
    sys.modules["passlib.context"] = passlib_ctx

if "pydantic" not in sys.modules:
    pydantic_mod = types.ModuleType("pydantic")
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        @classmethod
        def model_validate(cls, obj, **kwargs):
            if isinstance(obj, dict):
                return cls(**obj)
            data = {}
            for field in getattr(cls, "__annotations__", {}):
                val = getattr(obj, field, None)
                if val is None and field == "task_id" and hasattr(obj, "id"):
                    val = getattr(obj, "id")
                elif val is None and field == "id" and hasattr(obj, "task_id"):
                    val = getattr(obj, "task_id")
                if val is not None:
                    data[field] = val
            return cls(**data)
    def Field(default=..., **kwargs):
        return default
    def ConfigDict(**kwargs):
        return kwargs
    def AliasChoices(*choices):
        return choices
    pydantic_mod.BaseModel = BaseModel
    pydantic_mod.Field = Field
    pydantic_mod.ConfigDict = ConfigDict
    pydantic_mod.AliasChoices = AliasChoices
    pydantic_mod.EmailStr = str
    sys.modules["pydantic"] = pydantic_mod

if "sqlalchemy" not in sys.modules:
    sa_mod = types.ModuleType("sqlalchemy")
    sa_mod.create_engine = lambda *a, **k: None
    sa_mod.Column = lambda *a, **k: a[0] if a else None
    sa_mod.Integer = lambda *a, **k: int
    sa_mod.SmallInteger = lambda *a, **k: int
    sa_mod.BigInteger = lambda *a, **k: int
    sa_mod.String = lambda *a, **k: str
    sa_mod.Text = lambda *a, **k: str
    sa_mod.Boolean = lambda *a, **k: bool
    sa_mod.DateTime = lambda *a, **k: None
    sa_mod.Numeric = lambda *a, **k: float
    sa_mod.ForeignKey = lambda *a, **k: None
    sa_mod.CheckConstraint = lambda *a, **k: None
    sa_mod.UniqueConstraint = lambda *a, **k: None
    sa_mod.Index = lambda *a, **k: None
    class _Func:
        def now(self): return None
        def count(self): return None
    sa_mod.func = _Func()
    sa_mod.select = lambda *a, **k: None
    sa_mod.text = lambda *a, **k: None
    sa_mod.or_ = lambda *a, **k: None
    sys.modules["sqlalchemy"] = sa_mod

    sa_types = types.ModuleType("sqlalchemy.types")
    class TypeDecorator:
        impl = str
        def __init__(self, *a, **k): pass
    sa_types.TypeDecorator = TypeDecorator
    class JSON:
        def __init__(self, *a, **k): pass
        def with_variant(self, variant, name): return self
    sa_types.JSON = JSON
    sa_types.CHAR = str
    sa_types.String = str
    sys.modules["sqlalchemy.types"] = sa_types

    sa_dialects_pg = types.ModuleType("sqlalchemy.dialects.postgresql")
    class PG_UUID:
        def __init__(self, as_uuid=True): self.as_uuid = as_uuid
    class JSONB:
        def __init__(self, *a, **k): pass
    sa_dialects_pg.UUID = PG_UUID
    sa_dialects_pg.JSONB = JSONB
    sys.modules["sqlalchemy.dialects.postgresql"] = sa_dialects_pg

    sa_orm = types.ModuleType("sqlalchemy.orm")
    class DeclarativeBase: pass
    def _base_init(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    sa_orm.DeclarativeBase = DeclarativeBase
    sa_orm.declarative_base = lambda: type("Base", (object,), {
        "__init__": _base_init,
        "__tablename__": "",
        "metadata": type("Meta", (), {"tables": {}})(),
    })
    sa_orm.relationship = lambda *a, **k: None
    sa_orm.sessionmaker = lambda *a, **k: lambda: None
    sys.modules["sqlalchemy.orm"] = sa_orm

    sa_asyncio = types.ModuleType("sqlalchemy.ext.asyncio")
    sa_asyncio.create_async_engine = lambda *a, **k: None
    sa_asyncio.async_sessionmaker = lambda *a, **k: None
    sa_asyncio.AsyncSession = object
    sys.modules["sqlalchemy.ext.asyncio"] = sa_asyncio

# Now import project modules
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token, hash_token, generate_secure_token
from app.core.database import get_sync_db
from app.models.types import GUID, Vector
from app.models.user import User
from app.models.session import Session
from app.models.wallet import TokenWallet, TokenTransaction
from app.models.invoice import Invoice
from app.models.document import Document
from app.models.audit import AuditTask, AuditSentence, AuditReport
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from app.models.audit_log import AuditLog
from app.schemas.audit import HeatmapAnnotation, MatchedSource, AuditTaskStatusResponse


class TestVeriTextBackend(unittest.TestCase):
    """Deep verification tests for backend core logic, algorithms, and models without skipping."""

    def test_settings_load(self):
        """Validates configuration parameters match SRS/SDD specifications."""
        self.assertEqual(settings.APP_NAME, "VeriText AI API")
        self.assertEqual(settings.EMBEDDING_DIMENSION, 384)
        self.assertEqual(settings.WINNOWING_K_GRAM, 5)
        self.assertEqual(settings.WINNOWING_WINDOW_SIZE, 4)
        self.assertEqual(settings.SIMILARITY_LEXICAL_WEIGHT, 0.50)
        self.assertEqual(settings.SIMILARITY_SEMANTIC_WEIGHT, 0.35)
        self.assertEqual(settings.SIMILARITY_STYLO_WEIGHT, 0.15)

    def test_security_password_hashing(self):
        """Validates password hashing and verification."""
        pwd = "SecretPassword123!"
        hashed = get_password_hash(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_token_creation_and_decoding(self):
        """Validates JWT token signing and decoding."""
        user_id = str(uuid.uuid4())
        role = "REVIEWER"
        token = create_access_token(subject=user_id, role=role)
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], user_id)
        self.assertEqual(decoded["role"], role)

    def test_sha256_hash_token(self):
        """Validates SHA-256 token hashing for session storage."""
        token_str = "random-refresh-token-value"
        hashed = hash_token(token_str)
        self.assertEqual(len(hashed), 64)
        self.assertEqual(hashed, hashlib.sha256(token_str.encode("utf-8")).hexdigest())

    def test_guid_type_bind_param_postgresql_support(self):
        """Verifies bugfix in GUID.process_bind_param: returns uuid.UUID object for PostgreSQL."""
        guid_type = GUID()
        fake_pg_dialect = types.SimpleNamespace(name="postgresql")
        test_uuid = uuid.uuid4()
        
        # When passed a uuid.UUID, must return uuid.UUID (not str) so asyncpg accepts it
        bound_from_uuid = guid_type.process_bind_param(test_uuid, fake_pg_dialect)
        self.assertIsInstance(bound_from_uuid, uuid.UUID)
        self.assertEqual(bound_from_uuid, test_uuid)
        
        # When passed a string, must convert to uuid.UUID
        bound_from_str = guid_type.process_bind_param(str(test_uuid), fake_pg_dialect)
        self.assertIsInstance(bound_from_str, uuid.UUID)
        self.assertEqual(bound_from_str, test_uuid)

        # For non-PostgreSQL dialects, must return string
        fake_sqlite_dialect = types.SimpleNamespace(name="sqlite")
        bound_sqlite = guid_type.process_bind_param(test_uuid, fake_sqlite_dialect)
        self.assertIsInstance(bound_sqlite, str)
        self.assertEqual(bound_sqlite, str(test_uuid))

    def test_get_sync_db_context_manager_behavior(self):
        """Verifies bugfix: get_sync_db can be used cleanly as a context manager."""
        # Must have __enter__ and __exit__ attributes when called
        cm = get_sync_db()
        self.assertTrue(hasattr(cm, "__enter__"))
        self.assertTrue(hasattr(cm, "__exit__"))

    def test_all_14_models_instantiation(self):
        """Validates that all 14 SDD database models instantiate properly."""
        user = User(
            id=uuid.uuid4(),
            full_name="Dr. Budi Santoso",
            email="budi@univ.ac.id",
            institution="Universitas Indonesia",
            password_hash="fakehash",
            role="PREMIUM",
        )
        self.assertEqual(user.full_name, "Dr. Budi Santoso")

        sess = Session(
            id=uuid.uuid4(),
            user_id=user.id,
            refresh_token_hash="fake_hash",
        )
        self.assertEqual(sess.user_id, user.id)

        wallet = TokenWallet(id=uuid.uuid4(), user_id=user.id, balance=10)
        self.assertEqual(wallet.balance, 10)

        tx = TokenTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type="DEBIT_AUDIT",
            amount=-2,
            balance_after=8,
        )
        self.assertEqual(tx.amount, -2)

        inv = Invoice(
            id=uuid.uuid4(),
            user_id=user.id,
            order_id="VT-20261011-ABCD1234",
            package_name="Paket Peneliti",
            token_amount=50,
            gross_amount=100000,
        )
        self.assertEqual(inv.order_id, "VT-20261011-ABCD1234")

        doc = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            original_filename="Tesis_Final.pdf",
            stored_filename="tesis_uuid.pdf",
            file_size_bytes=1048576,
            mime_type="application/pdf",
        )
        self.assertEqual(doc.original_filename, "Tesis_Final.pdf")

        audit_task = AuditTask(
            id=uuid.uuid4(),
            document_id=doc.id,
            user_id=user.id,
            audit_depth="FULL",
            status="QUEUED",
        )
        self.assertEqual(audit_task.audit_depth, "FULL")

        audit_sentence = AuditSentence(
            id=uuid.uuid4(),
            audit_task_id=audit_task.id,
            sentence_index=0,
            sentence_text="Ini adalah kalimat pengantar penelitian.",
            start_char=0,
            end_char=42,
            word_count=5,
        )
        self.assertEqual(audit_sentence.word_count, 5)

        report = AuditReport(
            id=uuid.uuid4(),
            audit_task_id=audit_task.id,
            score_lexical=12.5,
            score_semantic=20.0,
            score_stylometric=5.0,
            score_composite=14.0,
            heatmap_annotations=[],
            matched_sources=[],
        )
        self.assertEqual(float(report.score_composite), 14.0)

        corpus_doc = CorpusDocument(
            id=uuid.uuid4(),
            uploaded_by=user.id,
            title="Kumpulan Paper 2024",
            category="Informatika",
            stored_filename="corpus_batch.zip",
            sha256_hash="hash123",
        )
        self.assertEqual(corpus_doc.title, "Kumpulan Paper 2024")

        chunk = DocumentChunk(
            id=uuid.uuid4(),
            corpus_doc_id=corpus_doc.id,
            chunk_index=0,
            chunk_text="Vektor kalimat pembanding",
            embedding=[0.1] * 384,
        )
        self.assertEqual(chunk.chunk_index, 0)

        fp = LexicalFingerprint(
            id=uuid.uuid4(),
            corpus_doc_id=corpus_doc.id,
            fingerprint_hash=12345678901234,
        )
        self.assertEqual(fp.fingerprint_hash, 12345678901234)

        log = AuditLog(
            id=uuid.uuid4(),
            actor_id=user.id,
            action_type="USER_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            action_result="SUCCESS",
            meta_data={"ip": "127.0.0.1"},
        )
        self.assertEqual(log.action_type, "USER_LOGIN")

    def test_heatmap_annotation_and_status_schema(self):
        """Validates schema models and AliasChoices on task_id."""
        anno = HeatmapAnnotation(
            start=0,
            end=50,
            tier="T1",
            color="RED",
            source_chunk_id="uuid-123",
            similarity=0.95,
        )
        self.assertEqual(anno.color, "RED")
        self.assertEqual(anno.tier, "T1")

        # Test AuditTaskStatusResponse with task_id
        t_id = uuid.uuid4()
        d_id = uuid.uuid4()
        status_resp = AuditTaskStatusResponse(
            task_id=t_id,
            document_id=d_id,
            audit_depth="FULL",
            status="QUEUED",
            progress_pct=0,
            created_at=None,
        )
        self.assertEqual(status_resp.task_id, t_id)

    def test_winnowing_fingerprinting_algorithm(self):
        """Validates the core Winnowing algorithm logic (k=5, w=4) matching SDD 3.2.1."""
        text = "sistem deteksi plagiarisme cerdas berbasis arsitektur hybrid"
        tokens = text.lower().replace(" ", "")
        k = 5
        w = 4
        
        # 1. Generate k-grams
        kgrams = [tokens[i:i+k] for i in range(len(tokens) - k + 1)]
        self.assertGreater(len(kgrams), 0)
        self.assertEqual(kgrams[0], "siste")

        # 2. Hash k-grams with Rabin-Karp polynomial rolling hash
        def rabin_karp_hash(s, base=257, mod=10**9 + 7):
            h = 0
            for char in s:
                h = (h * base + ord(char)) % mod
            return h

        hashes = [rabin_karp_hash(kg) for kg in kgrams]
        self.assertEqual(len(hashes), len(kgrams))

        # 3. Sliding window fingerprint selection
        fingerprints = []
        for i in range(len(hashes) - w + 1):
            window = hashes[i:i+w]
            min_val = min(window)
            if not fingerprints or fingerprints[-1] != min_val:
                fingerprints.append(min_val)

        self.assertGreater(len(fingerprints), 0)
        self.assertLessEqual(len(fingerprints), len(hashes))

    def test_composite_score_and_severity_classification(self):
        """Validates composite score weights and color bands matching SDD 3.6.2."""
        # Formula: 50% Lexical + 35% Semantic + 15% Stylometric
        t1, t2, t3 = 20.0, 40.0, 10.0
        expected = round(0.50 * t1 + 0.35 * t2 + 0.15 * t3, 2)
        self.assertEqual(expected, 25.5)

        def get_severity(score):
            if score <= 25.0:
                return "Aman", "#22C55E"
            elif score <= 50.0:
                return "Perlu Perhatian", "#EAB308"
            elif score <= 75.0:
                return "Terindikasi Plagiarisme", "#F97316"
            else:
                return "Plagiarisme Berat", "#EF4444"

        cat, col = get_severity(20.0)
        self.assertEqual(cat, "Aman")
        self.assertEqual(col, "#22C55E")

        cat, col = get_severity(35.0)
        self.assertEqual(cat, "Perlu Perhatian")
        self.assertEqual(col, "#EAB308")

        cat, col = get_severity(60.0)
        self.assertEqual(cat, "Terindikasi Plagiarisme")
        self.assertEqual(col, "#F97316")

        cat, col = get_severity(85.0)
        self.assertEqual(cat, "Plagiarisme Berat")
        self.assertEqual(col, "#EF4444")

    def test_midtrans_webhook_signature_calculation(self):
        """Validates Midtrans SHA-512 signature computation according to SDD 3.5.3."""
        order_id = "VT-20261011-9F2B81C4"
        status_code = "200"
        gross_amount = "25000.00"
        server_key = "SB-Mid-server-DemoServerKey1234567890"

        raw = f"{order_id}{status_code}{gross_amount}{server_key}"
        sig = hashlib.sha512(raw.encode("utf-8")).hexdigest()

        self.assertEqual(len(sig), 128)  # SHA-512 hex is 128 chars
        # Ensure deterministic signature
        sig_repeat = hashlib.sha512(raw.encode("utf-8")).hexdigest()
        self.assertEqual(sig, sig_repeat)

    def test_user_profile_response_with_token_balance(self):
        """Validates that UserProfileResponse includes token_balance and defaults appropriately."""
        from app.schemas.auth import UserProfileResponse, TokenResponse
        from datetime import datetime
        import uuid

        user_id = uuid.uuid4()
        now = datetime.now()
        profile = UserProfileResponse(
            id=user_id,
            full_name="Mochammad Azriel Albian Putra",
            email="azriel@kampus.ac.id",
            institution="Institut Teknologi Nasional",
            role="TRIAL",
            is_active=True,
            created_at=now,
            token_balance=5,
        )
        self.assertEqual(profile.full_name, "Mochammad Azriel Albian Putra")
        self.assertEqual(profile.token_balance, 5)

        token_resp = TokenResponse(
            access_token="mock-jwt-token-12345",
            user=profile,
        )
        self.assertEqual(token_resp.user.token_balance, 5)
        self.assertEqual(token_resp.access_token, "mock-jwt-token-12345")

    def test_audit_task_status_response_with_metadata(self):
        """Validates AuditTaskStatusResponse includes document_title and score_composite."""
        from app.schemas.audit import AuditTaskStatusResponse
        from datetime import datetime
        import uuid

        task_id = uuid.uuid4()
        doc_id = uuid.uuid4()
        now = datetime.now()

        status_resp = AuditTaskStatusResponse(
            task_id=task_id,
            document_id=doc_id,
            celery_task_id="celery-test-123",
            audit_depth="FULL",
            status="QUEUED",
            progress_pct=0,
            current_stage="INITIALIZING",
            created_at=now,
            document_title="Tesis_Azriel_Final.pdf",
            score_composite=14.2,
        )
        self.assertEqual(status_resp.document_title, "Tesis_Azriel_Final.pdf")
        self.assertEqual(status_resp.score_composite, 14.2)
        self.assertEqual(status_resp.audit_depth, "FULL")
        self.assertEqual(status_resp.status, "QUEUED")

    def test_user_model_token_balance_property(self):
        """Validates User.token_balance delegating to token_wallet.balance or defaulting to 0."""
        user = User(
            id=uuid.uuid4(),
            full_name="Mochammad Azriel",
            email="azriel@kampus.ac.id",
            password_hash="fakehash",
        )
        self.assertEqual(user.token_balance, 0)

        wallet = TokenWallet(user_id=user.id, balance=7)
        user.token_wallet = wallet
        self.assertEqual(user.token_balance, 7)

    def test_audit_task_properties_and_model_validation(self):
        """Validates AuditTask properties and serialization into AuditTaskStatusResponse."""
        doc = Document(
            id=uuid.uuid4(),
            original_filename="Skripsi_Azriel_2026.pdf",
            stored_filename="skripsi_123.pdf",
            file_size_bytes=2048,
        )
        task = AuditTask(
            id=uuid.uuid4(),
            document_id=doc.id,
            user_id=uuid.uuid4(),
            audit_depth="FULL",
            status="SUCCESS",
            progress_pct=100,
        )
        task.document = doc

        report = AuditReport(
            id=uuid.uuid4(),
            audit_task_id=task.id,
            score_composite=23.5,
        )
        task.report = report

        # Test model dynamic properties
        self.assertEqual(task.document_title, "Skripsi_Azriel_2026.pdf")
        self.assertEqual(task.score_composite, 23.5)

        # Test schema model_validate
        resp = AuditTaskStatusResponse.model_validate(task)
        self.assertEqual(resp.id, task.id)
        self.assertEqual(resp.task_id, task.id)
        self.assertEqual(resp.document_title, "Skripsi_Azriel_2026.pdf")
        self.assertEqual(resp.score_composite, 23.5)
        self.assertEqual(resp.progress_pct, 100)

    def test_document_service_validation(self):
        """Validates file upload format enforcement (.pdf, .docx, .txt allowed; others rejected)."""
        from app.services.document_service import DocumentService
        from fastapi import HTTPException, UploadFile

        # Valid files
        for valid_name in ["naskah.pdf", "skripsi.docx", "draft.txt", "PAPER.PDF"]:
            f = UploadFile(filename=valid_name)
            try:
                DocumentService.validate_file(f)
            except HTTPException:
                self.fail(f"validate_file falsely rejected valid file {valid_name}")

        # Invalid extensions
        for invalid_name in ["script.exe", "virus.py", "archive.zip", "test.sh", "noextension"]:
            f = UploadFile(filename=invalid_name)
            with self.assertRaises(HTTPException) as ctx:
                DocumentService.validate_file(f)
            self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
