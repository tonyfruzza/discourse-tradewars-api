import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    response = await client.get("/api/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_me_auto_enroll(client, auth_headers):
    response = await client.get("/api/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["credits"] == 20000
    assert data["sector_id"] == 1
    assert data["turns_remaining"] == 300


@pytest.mark.asyncio
async def test_me_returns_existing_player(client, auth_headers):
    # First call auto-enrolls
    await client.get("/api/me", headers=auth_headers)
    # Second call returns same player
    response = await client.get("/api/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["discourse_user_id"] == 1
