import time

import jwt as pyjwt
import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_expired_token_rejected(client):
    token = pyjwt.encode(
        {"discourse_user_id": 1, "username": "test", "admin": False, "exp": time.time() - 10},
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    resp = await client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_token_rejected(client):
    resp = await client.get("/api/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_missing_user_id_rejected(client):
    token = pyjwt.encode(
        {"username": "test", "admin": False},
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    resp = await client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "payload" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_auto_enrollment(client, auth_headers):
    resp = await client.get("/api/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["credits"] == 20000
    assert data["sector_id"] == 1


@pytest.mark.asyncio
async def test_admin_required_for_bigbang(client, auth_headers):
    resp = await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50},
        headers=auth_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_bigbang(client, admin_headers, db):
    resp = await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["sectors"] == 50
