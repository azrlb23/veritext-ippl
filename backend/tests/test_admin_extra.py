import unittest
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.api.v1 import admin_extra
from app.core.database import get_db
from app.main import app


class _FakeResult:
    def __init__(self, scalar_val=0, rows=None, first_row=None, scalars_list=None):
        self._scalar = scalar_val
        self._rows = rows or []
        self._first = first_row
        self._scalars = scalars_list or []

    def scalar(self):
        return self._scalar

    def all(self):
        return self._rows

    def first(self):
        return self._first

    def scalars(self):
        return SimpleNamespace(all=lambda: self._scalars)


def _make_user(role: str):
    return SimpleNamespace(
        id=uuid.uuid4(),
        email=f"{role.lower()}@veritext.test",
        full_name=f"{role} User",
        role=role,
        is_active=True,
    )


class TestAdminExtraRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.paths = [
            "/api/v1/admin/users",
            "/api/v1/admin/overview",
            "/api/v1/admin/invoices",
            "/api/v1/admin/system-extras",
        ]

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_admin_extra_router_only_get_methods(self):
        routes = list(admin_extra.router.routes)
        self.assertEqual(len(routes), 4)
        for route in routes:
            methods = getattr(route, "methods", set())
            self.assertEqual(methods, {"GET"})

        app.dependency_overrides[get_current_user] = lambda: _make_user("ADMIN")
        app.dependency_overrides[get_db] = lambda: AsyncMock()
        for path in self.paths:
            for fn in (self.client.post, self.client.put, self.client.patch, self.client.delete):
                resp = fn(path)
                self.assertEqual(resp.status_code, 405, f"Expected 405 for {fn.__name__} {path}")

    def test_non_admin_roles_receive_403_forbidden(self):
        app.dependency_overrides[get_db] = lambda: AsyncMock()
        for role in ("FREE", "PREMIUM"):
            app.dependency_overrides[get_current_user] = lambda r=role: _make_user(r)
            for path in self.paths:
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 403, f"{role} got {resp.status_code} on {path}")

    def test_admin_endpoints_return_200_and_strip_password_hash(self):
        now = datetime.now(timezone.utc)
        fake_user_row = SimpleNamespace(
            id=uuid.uuid4(), full_name="Tester", email="tester@veritext.test",
            role="FREE", is_active=True, lockout_until=None, created_at=now,
            balance=5, ai_trial_remaining=3, audit_count=2, password_hash="secret",
        )
        fake_invoice = SimpleNamespace(
            id=uuid.uuid4(), order_id="ORD-1", user_id=uuid.uuid4(),
            package_name="Paket Starter", token_amount=15, gross_amount=25000,
            payment_method="qris", status="SETTLEMENT", paid_at=now, created_at=now,
        )
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(
            side_effect=[
                _FakeResult(scalar_val=1),
                _FakeResult(rows=[fake_user_row]),
                _FakeResult(scalar_val=3),
                _FakeResult(scalar_val=4),
                _FakeResult(scalar_val=12),
                _FakeResult(rows=[("FREE", 5), ("PREMIUM", 2)]),
                _FakeResult(rows=[]),
                _FakeResult(rows=[]),
                _FakeResult(scalar_val=25000),
                _FakeResult(scalar_val=1),
                _FakeResult(scalar_val=0),
                _FakeResult(scalar_val=0),
                _FakeResult(first_row=("Paket Starter",)),
                _FakeResult(scalar_val=1),
                _FakeResult(scalars_list=[fake_invoice]),
                _FakeResult(scalar_val=1),
                _FakeResult(scalar_val=2),
                _FakeResult(scalar_val=0),
            ]
        )
        app.dependency_overrides[get_current_user] = lambda: _make_user("ADMIN")
        app.dependency_overrides[get_db] = lambda: mock_db

        r_users = self.client.get("/api/v1/admin/users")
        self.assertEqual(r_users.status_code, 200)
        self.assertNotIn("password_hash", r_users.text)
        self.assertEqual(len(r_users.json()["data"]["items"]), 1)

        r_overview = self.client.get("/api/v1/admin/overview?days=7")
        self.assertEqual(r_overview.status_code, 200)
        self.assertEqual(len(r_overview.json()["data"]["trends"]), 7)

        r_invoices = self.client.get("/api/v1/admin/invoices")
        self.assertEqual(r_invoices.status_code, 200)
        self.assertEqual(r_invoices.json()["data"]["summary"]["total_revenue"], 25000)

        r_sys = self.client.get("/api/v1/admin/system-extras")
        self.assertEqual(r_sys.status_code, 200)
        self.assertEqual(r_sys.json()["data"]["queued_audits"], 2)
