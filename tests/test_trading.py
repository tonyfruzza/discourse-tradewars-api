import pytest

from app.services.trading import calculate_price


def test_price_formula_low_stock():
    """Low stock = high price."""
    price = calculate_price(base_price=100, volatility=20, quantity=100, max_quantity=1000)
    assert price > 100


def test_price_formula_high_stock():
    """High stock = low price."""
    price = calculate_price(base_price=100, volatility=20, quantity=900, max_quantity=1000)
    assert price < 110


def test_price_formula_empty_stock():
    """Empty stock = maximum price."""
    price = calculate_price(base_price=100, volatility=20, quantity=0, max_quantity=1000)
    assert price == 120  # base * (1 + 0.20)


def test_price_formula_full_stock():
    """Full stock = base price."""
    price = calculate_price(base_price=100, volatility=20, quantity=1000, max_quantity=1000)
    assert price == 100


@pytest.mark.asyncio
async def test_buy_from_port(client, admin_headers, auth_headers):
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Sector 37 has a port and is 1 hop from sector 1 (verified with seed 42)
    # First check what warps sector 1 has
    sector_resp = await client.get("/api/sector", headers=auth_headers)
    warps = sector_resp.json()["warps"]

    # Find a warp target that has a port
    port_sector = None
    for target in warps:
        target_resp = await client.get(f"/api/sector/{target}", headers=auth_headers)
        if target_resp.json().get("port"):
            port_sector = target
            break

    if not port_sector:
        # Try 2-hop: warp to a non-fed sector, then check its warps
        for target in warps:
            if target > 10:
                await client.post(
                    "/api/sector/warp",
                    json={"target_sector_id": target},
                    headers=auth_headers,
                )
                inner = await client.get("/api/sector", headers=auth_headers)
                for inner_target in inner.json()["warps"]:
                    inner_resp = await client.get(
                        f"/api/sector/{inner_target}", headers=auth_headers
                    )
                    if inner_resp.json().get("port"):
                        await client.post(
                            "/api/sector/warp",
                            json={"target_sector_id": inner_target},
                            headers=auth_headers,
                        )
                        port_sector = inner_target
                        break
                if port_sector:
                    break
        if not port_sector:
            pytest.skip("Could not find a port within 2 hops")
    else:
        # Warp to the port sector
        resp = await client.post(
            "/api/sector/warp",
            json={"target_sector_id": port_sector},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    # Now at port sector - get port info
    port_resp = await client.get("/api/port", headers=auth_headers)
    assert port_resp.status_code == 200
    port_data = port_resp.json()

    # Find a sellable commodity
    sell_item = None
    for item in port_data["stock"]:
        if item["mode"] == "sell" and item["quantity"] > 0:
            sell_item = item
            break

    if not sell_item:
        pytest.skip("Port has no sellable items")

    # Buy 1 unit
    trade_resp = await client.post(
        "/api/port/trade",
        json={
            "commodity_id": sell_item["commodity_id"],
            "action": "buy",
            "quantity": 1,
        },
        headers=auth_headers,
    )
    assert trade_resp.status_code == 200
    data = trade_resp.json()
    assert data["action"] == "buy"
    assert data["quantity"] == 1
    assert data["credits_remaining"] < 20000


@pytest.mark.asyncio
async def test_hold_capacity_limit(client, admin_headers, auth_headers):
    """Cannot buy more than ship holds allow."""
    await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    await client.get("/api/me", headers=auth_headers)

    # Try to buy 999 units — should fail on hold capacity
    # First navigate to a port
    sector_resp = await client.get("/api/sector", headers=auth_headers)
    for target in sector_resp.json()["warps"]:
        target_resp = await client.get(f"/api/sector/{target}", headers=auth_headers)
        if target_resp.json().get("port"):
            await client.post(
                "/api/sector/warp",
                json={"target_sector_id": target},
                headers=auth_headers,
            )
            port_resp = await client.get("/api/port", headers=auth_headers)
            if port_resp.status_code == 200:
                for item in port_resp.json()["stock"]:
                    if item["mode"] == "sell" and item["quantity"] > 0:
                        trade_resp = await client.post(
                            "/api/port/trade",
                            json={
                                "commodity_id": item["commodity_id"],
                                "action": "buy",
                                "quantity": 999,
                            },
                            headers=auth_headers,
                        )
                        # Should fail — either holds or port stock
                        assert trade_resp.status_code == 400
                        return

    pytest.skip("No port with sellable items found")
