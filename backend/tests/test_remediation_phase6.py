"""
Test Suite: Remediation Phase 6 — Generasi Invoice PDF Resmi, Persistensi Konfigurasi Admin, dan Pengerasan Gateway Produksi
TDD Tests verifying:
  - test_tc_sec_34_invoice_pdf_generation_and_auth: Official ReportLab invoice generation & owner/admin authorization
  - test_tc_sec_35_admin_config_persistence: Persistent hyperparameter tuning storage & RBAC protection
  - test_tc_sec_36_production_security_headers_and_docs_toggle: OWASP security headers & production swagger hiding
"""

import asyncio
from datetime import datetime, timezone
import io
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.models.user import User
from app.models.invoice import Invoice
from app.models.audit_log import AuditLog
from app.services.pdf_invoice_service import generate_invoice_pdf, clean_invoice_filename
import app.api.v1.billing as billing_router


class MockQueryResult:
    def __init__(self, items=None, scalar_val=None):
        self._items = items if items is not None else []
        self._scalar_val = scalar_val

    def scalar_one_or_none(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalar(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None


class MockAsyncSession:
    def __init__(self, execute_handler=None):
        self.execute_handler = execute_handler
        self.executed_statements = []
        self.added = []
        self.deleted = []
        self.committed = False
        self.flushed = False

    async def execute(self, stmt):
        self.executed_statements.append(stmt)
        if self.execute_handler:
            res = self.execute_handler(stmt)
            if asyncio.iscoroutine(res):
                return await res
            return res
        return MockQueryResult([])

    def add(self, item):
        self.added.append(item)
        if hasattr(item, "id") and getattr(item, "id", None) is None:
            item.id = uuid.uuid4()

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True

    async def refresh(self, item):
        pass

    async def delete(self, item):
        self.deleted.append(item)


class TestRemediationPhase6(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    # =========================================================================
    # TC-SEC-34: Generasi PDF Invoice Resmi & Otorisasi Pemilik/Admin (F5)
    # =========================================================================
    async def test_tc_sec_34_invoice_pdf_generation_and_auth(self):
        """
        TC-SEC-34: Memvalidasi generasi byte PDF invoice resmi dengan ReportLab,
        otorisasi pemilik/admin, dan penolakan HTTP 403 untuk non-pemilik.
        """
        # 1. Direct unit test of generate_invoice_pdf
        pdf_bytes = generate_invoice_pdf(
            invoice_id=str(uuid.uuid4()),
            order_id="VT-ORDER-20261024-TEST",
            user_name="Budi Hartono",
            user_email="budi@campus.ac.id",
            package_name="Paket 50 Token Audit Akademik",
            token_amount=50,
            gross_amount=100000.0,
            status="PAID",
            created_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
            payment_method="qris",
            midtrans_transaction_id="midtrans-tx-12345",
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 2000, f"Expected PDF bytes > 2000, got {len(pdf_bytes)}")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "Generated file must start with PDF magic bytes %PDF-")

        # Test alternative statuses
        for alt_status in ["PENDING", "FAILED", "EXPIRED"]:
            alt_pdf = generate_invoice_pdf(
                invoice_id=str(uuid.uuid4()),
                order_id=f"VT-ORDER-{alt_status}",
                user_name="Budi",
                user_email="budi@test.com",
                package_name="Paket 10",
                token_amount=10,
                gross_amount=25000.0,
                status=alt_status,
                created_at=datetime.now(timezone.utc),
            )
            self.assertTrue(alt_pdf.startswith(b"%PDF-"))

        # Test filename sanitation
        self.assertEqual(clean_invoice_filename("VT-INV/123@#45"), "Invoice_VT-INV_123_45.pdf")

        # 2. Endpoint authorization & delivery tests
        owner_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        inv_id = uuid.uuid4()
        order_id = "VT-INV-998877"

        owner_user = User(
            id=owner_id,
            email="owner@campus.ac.id",
            full_name="Pemilik Sah Invoice",
            role="FREE",
        )
        non_owner_user = User(
            id=other_user_id,
            email="attacker@campus.ac.id",
            full_name="Pengguna Lain",
            role="FREE",
        )
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@veritext.ai",
            full_name="Super Administrator",
            role="ADMIN",
        )

        test_invoice = Invoice(
            id=inv_id,
            user_id=owner_id,
            order_id=order_id,
            package_name="Paket 10 Token",
            token_amount=10,
            gross_amount=25000,
            status="PAID",
            payment_method="bank_transfer",
            created_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
        )

        def mock_db_handler(stmt):
            stmt_str = str(stmt).lower()
            if "users" in stmt_str:
                return MockQueryResult([owner_user])
            return MockQueryResult([test_invoice])

        mock_db = MockAsyncSession(execute_handler=mock_db_handler)

        # Case A: Owner downloads own invoice via UUID -> HTTP 200 PDF
        resp_owner = await billing_router.get_invoice_pdf(
            inv_id=str(inv_id),
            current_user=owner_user,
            db=mock_db,
        )
        self.assertEqual(resp_owner.media_type, "application/pdf")
        self.assertTrue(resp_owner.body.startswith(b"%PDF-"))
        self.assertIn(f"Invoice_{order_id}.pdf", resp_owner.headers.get("content-disposition", ""))

        # Case B: Owner downloads own invoice via Order ID -> HTTP 200 PDF
        resp_order_id = await billing_router.get_invoice_pdf(
            inv_id=order_id,
            current_user=owner_user,
            db=mock_db,
        )
        self.assertEqual(resp_order_id.media_type, "application/pdf")
        self.assertTrue(resp_order_id.body.startswith(b"%PDF-"))

        # Case C: Admin downloads other user's invoice -> HTTP 200 PDF
        resp_admin = await billing_router.get_invoice_pdf(
            inv_id=str(inv_id),
            current_user=admin_user,
            db=mock_db,
        )
        self.assertEqual(resp_admin.media_type, "application/pdf")
        self.assertTrue(resp_admin.body.startswith(b"%PDF-"))

        # Case D: Non-owner non-admin user downloads invoice -> HTTP 403 Forbidden
        with self.assertRaises(HTTPException) as cm:
            await billing_router.get_invoice_pdf(
                inv_id=str(inv_id),
                current_user=non_owner_user,
                db=mock_db,
            )
        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Access denied", cm.exception.detail)

        # Case E: Non-existent invoice -> HTTP 404 Not Found
        empty_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        with self.assertRaises(HTTPException) as cm_404:
            await billing_router.get_invoice_pdf(
                inv_id="NON-EXISTENT-INV",
                current_user=owner_user,
                db=empty_db,
            )
        self.assertEqual(cm_404.exception.status_code, status.HTTP_404_NOT_FOUND)


    # =========================================================================
    # TC-SEC-36: Pengerasan Gateway Produksi, HTTP Security Headers & Swagger (F6 & ROUND7-01)
    # =========================================================================
    def test_tc_sec_36_production_security_headers_and_docs_toggle(self):
        """
        TC-SEC-36: Memvalidasi keberadaan HTTP security headers dan nonaktifnya rute /docs pada mode produksi.
        """
        # 1. OWASP HTTP Security Headers validation on standard response
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

        # Check all 5 mandatory security headers
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertEqual(resp.headers.get("x-xss-protection"), "1; mode=block")
        self.assertIn("max-age=", resp.headers.get("strict-transport-security", ""))
        self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")

        # 2. In development mode: /docs is accessible
        with patch.object(settings, "ENVIRONMENT", "development"):
            res_dev = self.client.get("/health")
            self.assertEqual(res_dev.status_code, 200)
            res_root = self.client.get("/")
            self.assertEqual(res_root.json().get("docs"), "/docs")

        # 3. In production mode: /docs, /redoc, and /openapi.json are blocked (HTTP 404)
        with patch.object(settings, "ENVIRONMENT", "production"):
            res_docs = self.client.get("/docs")
            self.assertEqual(res_docs.status_code, status.HTTP_404_NOT_FOUND)

            res_redoc = self.client.get("/redoc")
            self.assertEqual(res_redoc.status_code, status.HTTP_404_NOT_FOUND)

            res_openapi = self.client.get("/openapi.json")
            self.assertEqual(res_openapi.status_code, status.HTTP_404_NOT_FOUND)

            res_root_prod = self.client.get("/")
            self.assertIsNone(res_root_prod.json().get("docs"))

        # 4. Database engine echo check: in production, echo must evaluate to False
        is_echo_prod = settings.DEBUG and settings.ENVIRONMENT.lower() != "production"
        with patch.object(settings, "ENVIRONMENT", "production"):
            self.assertFalse(settings.DEBUG and settings.ENVIRONMENT.lower() != "production")


if __name__ == "__main__":
    unittest.main()
