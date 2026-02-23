import pytest


@pytest.mark.asyncio
async def test_warp_to_adjacent_sector(client, admin_headers, auth_headers):
    # Generate galaxy via API
    resp = await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    # Auto-enroll player (sector 1)
    await client.get("/api/me", headers=auth_headers)

    # Get warps from sector 1
    sector = await client.get("/api/sector", headers=auth_headers)
    assert sector.status_code == 200
    warps = sector.json()["warps"]
    assert len(warps) > 0

    # Warp to first adjacent sector
    target = warps[0]
    resp = await client.post(
        "/api/sector/warp",
        json={"target_sector_id": target},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["moved_to"] == target


@pytest.mark.asyncio
async def test_warp_non_adjacent_rejected(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Try to warp to sector 50 (not adjacent to sector 1)
    resp = await client.post(
        "/api/sector/warp",
        json={"target_sector_id": 50},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "No warp" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_warp_deducts_turns(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )

    me = await client.get("/api/me", headers=auth_headers)
    initial_turns = me.json()["turns_remaining"]

    sector = await client.get("/api/sector", headers=auth_headers)
    target = sector.json()["warps"][0]

    resp = await client.post(
        "/api/sector/warp",
        json={"target_sector_id": target},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["turns_remaining"] < initial_turns
