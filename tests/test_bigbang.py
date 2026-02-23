import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.bigbang.generator import bigbang
from app.bigbang.topology import build_adjacency, find_components
from app.models.commodity import Commodity
from app.models.port import Port, PortStock, PortType
from app.models.sector import Sector, SectorWarp
from app.models.ship import ShipType


@pytest.mark.asyncio
async def test_bigbang_creates_sectors(db):
    result = await bigbang(db, galaxy_size=50, seed=42)
    assert result["sectors"] == 50
    assert result["fedspace_sectors"] == 10

    count = (await db.execute(select(func.count(Sector.id)))).scalar()
    assert count == 50


@pytest.mark.asyncio
async def test_bigbang_creates_fedspace(db):
    await bigbang(db, galaxy_size=50, seed=42)

    fedspace = (await db.execute(
        select(Sector).where(Sector.is_fedspace.is_(True))
    )).scalars().all()
    assert len(fedspace) == 10
    assert all(s.id <= 10 for s in fedspace)


@pytest.mark.asyncio
async def test_bigbang_seeds_lookup_tables(db):
    await bigbang(db, galaxy_size=50, seed=42)

    commodities = (await db.execute(select(func.count(Commodity.id)))).scalar()
    assert commodities == 3

    port_types = (await db.execute(select(func.count(PortType.id)))).scalar()
    assert port_types == 8

    ship_types = (await db.execute(select(func.count(ShipType.id)))).scalar()
    assert ship_types == 3


@pytest.mark.asyncio
async def test_bigbang_generates_connected_graph(db):
    await bigbang(db, galaxy_size=50, seed=42)

    warps = (await db.execute(
        select(SectorWarp.from_sector_id, SectorWarp.to_sector_id)
    )).all()
    adj = build_adjacency([(w[0], w[1]) for w in warps], 50)
    components = find_components(adj, 50)
    assert len(components) == 1, f"Galaxy has {len(components)} disconnected components"


@pytest.mark.asyncio
async def test_bigbang_generates_ports(db):
    result = await bigbang(db, galaxy_size=50, seed=42)
    assert result["ports"] > 0

    # No ports in FedSpace
    fedspace_ports = (await db.execute(
        select(func.count(Port.id)).join(Sector).where(Sector.is_fedspace.is_(True))
    )).scalar()
    assert fedspace_ports == 0


@pytest.mark.asyncio
async def test_bigbang_port_stock_integrity(db):
    await bigbang(db, galaxy_size=50, seed=42)

    stocks = (await db.execute(select(PortStock))).scalars().all()
    assert len(stocks) > 0

    for stock in stocks:
        assert 0 <= stock.quantity <= stock.max_quantity
        assert stock.mode in ("buy", "sell")


@pytest.mark.asyncio
async def test_bigbang_fedspace_warps(db):
    await bigbang(db, galaxy_size=50, seed=42)

    warps_from_1 = (await db.execute(
        select(SectorWarp.to_sector_id).where(SectorWarp.from_sector_id == 1)
    )).scalars().all()
    assert set(warps_from_1) >= {2, 3, 4, 5, 6, 7}


@pytest.mark.asyncio
async def test_bigbang_via_api(client, admin_headers):
    resp = await client.post(
        "/api/admin/bigbang",
        json={"galaxy_size": 50, "seed": 42},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["sectors"] == 50
    assert data["ports"] > 0
    assert data["commodities"] == 3
