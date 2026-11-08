import unittest
from unittest.mock import AsyncMock

from app.api.v1.admin import router
from app.schemas.admin import SystemHealthMetricsResponse
from app.services.admin_monitoring_service import (
    get_analytics,
    get_system_health_metrics,
    get_transactions,
)


class MockResult:
    def __init__(self, scalar_val=5, items=None):
        self._scalar = scalar_val
        self._items = items or []

    def scalar(self):
        return self._scalar

    def scalars(self):
        return self

    def all(self):
        return self._items


class TestAdminReadOnly(unittest.IsolatedAsyncioTestCase):
    def test_admin_routes_are_strictly_get_only(self):
        forbidden_methods = {"POST", "PUT", "PATCH", "DELETE"}
        routes = list(router.routes)
        self.assertGreaterEqual(len(routes), 5)
        for route in routes:
            route_methods = getattr(route, "methods", set())
            intersect = route_methods.intersection(forbidden_methods)
            self.assertEqual(
                len(intersect), 0,
                f"Route {getattr(route, 'path', '')} has non-GET methods: {intersect}",
            )
            self.assertTrue("GET" in route_methods)

    async def test_get_analytics(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockResult(scalar_val=42))
        analytics = await get_analytics(mock_db)
        self.assertIsInstance(analytics, dict)
        for key in ("total_documents", "avg_similarity", "total_revenue", "active_users"):
            self.assertIn(key, analytics)
        self.assertEqual(analytics["total_documents"], 42)
        self.assertEqual(analytics["avg_similarity"], 42.0)
        self.assertEqual(analytics["total_revenue"], 42)
        self.assertEqual(analytics["active_users"], 42)

    async def test_get_transactions(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockResult(scalar_val=1000, items=[]))
        tx = await get_transactions(mock_db, limit=20)
        self.assertIsInstance(tx, dict)
        self.assertIn("total_revenue", tx)
        self.assertIn("items", tx)
        self.assertEqual(tx["total_revenue"], 1000)
        self.assertIsInstance(tx["items"], list)

    async def test_get_system_health_metrics(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockResult(scalar_val=3))
        metrics = await get_system_health_metrics(mock_db)
        self.assertIsInstance(metrics, SystemHealthMetricsResponse)
        self.assertEqual(metrics.database_status, "HEALTHY")
        self.assertEqual(metrics.celery_workers, 1)
        self.assertEqual(metrics.queue_depth, 0)
        self.assertEqual(metrics.redis_mem_mb, 12.5)
        self.assertGreaterEqual(metrics.pgvector_latency_ms, 0)
        dump = metrics.model_dump()
        self.assertIn("celery_workers", dump)
        self.assertIn("queue_depth", dump)
        self.assertIn("redis_mem_mb", dump)
        self.assertIn("pgvector_latency_ms", dump)
