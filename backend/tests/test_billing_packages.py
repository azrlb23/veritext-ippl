from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.billing_packages import PACKAGES, resolve_package


def test_bundles_follow_agents_pricing():
    assert resolve_package("pkg_starter") == {"name": "Paket Starter", "tokens": 15, "price": 25000}
    assert PACKAGES["pkg_skripsi_pro"]["tokens"] == 50 and PACKAGES["pkg_skripsi_pro"]["price"] == 65000
    assert PACKAGES["pkg_riset_intensif"]["tokens"] == 150 and PACKAGES["pkg_riset_intensif"]["price"] == 150000


def test_unit_purchase_is_two_thousand_per_token_min_five():
    pkg = resolve_package("pkg_tokens", 5)
    assert pkg["tokens"] == 5 and pkg["price"] == 10000
    assert resolve_package("pkg_tokens", 12)["price"] == 24000


@pytest.mark.parametrize("amount", [None, 0, 4, 501])
def test_unit_purchase_rejects_out_of_range(amount):
    with pytest.raises(HTTPException) as exc:
        resolve_package("pkg_tokens", amount)
    assert exc.value.status_code == 400


def test_unknown_package_rejected():
    with pytest.raises(HTTPException):
        resolve_package("pkg_10token")
