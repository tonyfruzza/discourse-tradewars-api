import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_tick_requires_api_key(client):
    resp = await client.post("/api/tick")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_tick_rejects_wrong_key(client):
    resp = await client.post(
        "/api/tick",
        headers={"X-Tick-Api-Key": "wrong-key"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_tick_regenerates_turns(client, admin_headers, auth_headers):
    # Generate galaxy and enroll player
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Use some turns by warping
    sector = await client.get("/api/sector", headers=auth_headers)
    target = sector.json()["warps"][0]
    await client.post(
        "/api/sector/warp",
        json={"target_sector_id": target},
        headers=auth_headers,
    )

    # Verify turns decreased
    me = await client.get("/api/me", headers=auth_headers)
    assert me.json()["turns_remaining"] < settings.TURNS_PER_DAY

    # Run tick
    tick_headers = {"X-Tick-Api-Key": settings.TICK_API_KEY}
    resp = await client.post("/api/tick", headers=tick_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["players_updated"] > 0
    assert data["turns_per_day"] == settings.TURNS_PER_DAY

    # Verify turns regenerated
    me = await client.get("/api/me", headers=auth_headers)
    assert me.json()["turns_remaining"] == settings.TURNS_PER_DAY
