import pytest


@pytest.mark.asyncio
async def test_pathfind_same_sector(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    resp = await client.get("/api/pathfind?src=1&to=1", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["path"] == [1]
    assert data["hops"] == 0


@pytest.mark.asyncio
async def test_pathfind_adjacent_sectors(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Sector 1 → 2 (always adjacent in FedSpace)
    resp = await client.get("/api/pathfind?src=1&to=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["hops"] == 1
    assert data["path"] == [1, 2]


@pytest.mark.asyncio
async def test_pathfind_multi_hop(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Sector 1 → 10 (through FedSpace)
    resp = await client.get("/api/pathfind?src=1&to=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["hops"] >= 1
    assert data["path"][0] == 1
    assert data["path"][-1] == 10
