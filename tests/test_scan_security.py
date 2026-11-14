import asyncio

import pytest
from fastapi import HTTPException

from app.config import settings
from app.main import scan


def test_scan_endpoint_disabled_without_admin_key(monkeypatch):
    monkeypatch.setattr(settings, "scan_api_key", "")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(scan(""))
    assert exc.value.status_code == 503


def test_scan_endpoint_rejects_invalid_admin_key(monkeypatch):
    monkeypatch.setattr(settings, "scan_api_key", "correct-secret")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(scan("wrong-secret"))
    assert exc.value.status_code == 401
