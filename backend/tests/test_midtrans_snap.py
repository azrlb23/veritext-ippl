from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import settings
from app.services import midtrans_snap


async def test_snap_disabled_with_demo_key_makes_no_network_call():
    with patch.object(settings, "MIDTRANS_SERVER_KEY", "SB-Mid-server-DemoServerKey1234567890"), patch("httpx.AsyncClient") as client:
        assert midtrans_snap.snap_enabled() is False
        assert await midtrans_snap.create_snap_token("VT-1", 25000, "Starter", 15, {}) is None
        client.assert_not_called()


async def test_snap_token_returned_when_key_real():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"token": "tok-123"}
    http = MagicMock()
    http.post = AsyncMock(return_value=response)
    http.__aenter__ = AsyncMock(return_value=http)
    http.__aexit__ = AsyncMock(return_value=False)
    with patch.object(settings, "MIDTRANS_SERVER_KEY", "SB-Mid-server-realkey"), patch("httpx.AsyncClient", return_value=http):
        token = await midtrans_snap.create_snap_token("VT-1", 25000, "Starter", 15, {"email": "a@b.c"})
    assert token == "tok-123"
    body = http.post.call_args.kwargs["json"]
    assert body["transaction_details"] == {"order_id": "VT-1", "gross_amount": 25000}
