"""Galaxy generation orchestrator — the BigBang."""

import random

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.bigbang.namegen import generate_unique_names
from app.bigbang.seed_data import (
    COMMODITIES,
    FEDSPACE_WARPS,
    PORT_TYPE_WEIGHTS,
    PORT_TYPES,
    SHIP_TYPES,
)
from app.bigbang.topology import (
    bridge_components,
    build_adjacency,
    generate_warps,
)
from app.models.commodity import Commodity
from app.models.config import GameConfig
from app.models.player import Player
from app.models.port import Port, PortStock, PortType
from app.models.sector import Sector, SectorWarp
from app.models.ship import Ship, ShipCargo, ShipType
from app.models.trade_log import TradeLog


async def wipe_universe(db: AsyncSession) -> None:
    """Delete all game state tables in dependency order."""
    await db.execute(delete(TradeLog))
    await db.execute(delete(ShipCargo))
    await db.execute(delete(PortStock))
    await db.execute(delete(Port))
    await db.execute(delete(SectorWarp))
    # Unlink players from ships before deleting those
    await db.execute(text("UPDATE players SET ship_id = NULL"))
    await db.execute(delete(Ship))
    await db.execute(delete(Sector))
    await db.execute(delete(Player))
    await db.execute(delete(Commodity))
    await db.execute(delete(PortType))
    await db.execute(delete(ShipType))
    await db.execute(delete(GameConfig))
    await db.flush()


async def seed_lookup_tables(db: AsyncSession) -> None:
    """Insert commodities, port types, and ship types."""
    for code, name, base_price, volatility, illegal in COMMODITIES:
        db.add(Commodity(
            code=code, name=name, base_price=base_price,
            volatility=volatility, illegal=illegal,
        ))

    for pt_id, code, name, ore_mode, org_mode, equ_mode in PORT_TYPES:
        db.add(PortType(
            id=pt_id, code=code, name=name,
            ore_mode=ore_mode, org_mode=org_mode, equ_mode=equ_mode,
        ))

    for st_id, name, holds, cost, max_fighters, max_shields, offense, defense in SHIP_TYPES:
        db.add(ShipType(
            id=st_id, name=name, holds=holds, cost=cost,
            max_fighters=max_fighters, max_shields=max_shields,
            offense=offense, defense=defense,
        ))

    await db.flush()


async def create_sectors(
    db: AsyncSession, galaxy_size: int, rng: random.Random
) -> list[Sector]:
    """Phase 1: Create sectors with names. Sectors 1-10 are FedSpace."""
    names = generate_unique_names(galaxy_size, rng)
    sectors = []
    # Special FedSpace names
    fedspace_names = [
        "Terra", "Alpha Centauri", "Rylos", "Canopus", "Sol Gate",
        "Proxima", "Stardock Approach", "Nav Point Alpha", "Nav Point Beta", "Outpost"
    ]
    for i in range(galaxy_size):
        sector_id = i + 1
        is_fed = sector_id <= 10
        name = fedspace_names[i] if is_fed else names[i]
        sector = Sector(id=sector_id, name=name, is_fedspace=is_fed)
        db.add(sector)
        sectors.append(sector)
    await db.flush()
    return sectors


async def wire_warps(
    db: AsyncSession, galaxy_size: int, rng: random.Random
) -> dict[int, set[int]]:
    """Phase 2+3: Wire FedSpace canonical warps + random warps for the rest."""
    all_warps: list[tuple[int, int]] = list(FEDSPACE_WARPS)

    # Generate random warps for non-FedSpace
    random_warps = generate_warps(galaxy_size, fedspace_count=10, rng=rng)
    all_warps.extend(random_warps)

    # Deduplicate
    warp_set = set(all_warps)

    # Build adjacency and bridge any disconnected components
    adj = build_adjacency(list(warp_set), galaxy_size)
    bridges = bridge_components(adj, galaxy_size, rng=rng)
    warp_set.update(bridges)

    # Insert all warps
    for from_id, to_id in warp_set:
        db.add(SectorWarp(from_sector_id=from_id, to_sector_id=to_id))
    await db.flush()

    return build_adjacency(list(warp_set), galaxy_size)


async def generate_ports(
    db: AsyncSession, galaxy_size: int, rng: random.Random
) -> None:
    """Phase 4: Generate ports in ~60% of non-FedSpace sectors."""
    port_chance = 0.6
    max_stock = 1000

    for sector_id in range(11, galaxy_size + 1):
        if rng.random() > port_chance:
            continue

        # Pick port type using weights
        port_type_id = rng.choices(range(1, 9), weights=PORT_TYPE_WEIGHTS, k=1)[0]
        port_type = PORT_TYPES[port_type_id - 1]
        _, code, pt_name, ore_mode, org_mode, equ_mode = port_type

        port = Port(
            sector_id=sector_id,
            name=f"Port {sector_id}",
            port_type_id=port_type_id,
            cash=rng.randint(50000, 200000),
        )
        db.add(port)
        await db.flush()

        # Create stock for each commodity
        modes = [ore_mode, org_mode, equ_mode]
        for commodity_idx, mode in enumerate(modes):
            commodity_id = commodity_idx + 1  # ORE=1, ORG=2, EQU=3
            if mode == "sell":
                # Port sells: high initial stock
                qty = rng.randint(int(max_stock * 0.6), int(max_stock * 0.95))
            else:
                # Port buys: low initial stock
                qty = rng.randint(0, int(max_stock * 0.1))

            db.add(PortStock(
                port_id=port.id,
                commodity_id=commodity_id,
                quantity=qty,
                max_quantity=max_stock,
                mode=mode,
            ))

    await db.flush()


async def bigbang(db: AsyncSession, galaxy_size: int = 500, seed: int | None = None) -> dict:
    """Full galaxy generation: wipe, seed, create, wire, populate.

    Returns summary statistics.
    """
    rng = random.Random(seed)

    # Wipe everything
    await wipe_universe(db)

    # Seed lookup tables
    await seed_lookup_tables(db)

    # Phase 1: Create sectors
    await create_sectors(db, galaxy_size, rng)

    # Phase 2+3: Wire warps
    await wire_warps(db, galaxy_size, rng)

    # Phase 4: Generate ports
    await generate_ports(db, galaxy_size, rng)

    # Store config
    db.add(GameConfig(key="galaxy_size", value=str(galaxy_size)))
    db.add(GameConfig(key="galaxy_seed", value=str(seed or "random")))

    await db.commit()

    # Gather stats
    from sqlalchemy import func, select

    port_count = (await db.execute(select(func.count(Port.id)))).scalar() or 0
    warp_count = (await db.execute(select(func.count(SectorWarp.id)))).scalar() or 0

    return {
        "sectors": galaxy_size,
        "fedspace_sectors": 10,
        "ports": port_count,
        "warps": warp_count,
        "ship_types": len(SHIP_TYPES),
        "commodities": len(COMMODITIES),
        "port_types": len(PORT_TYPES),
    }
