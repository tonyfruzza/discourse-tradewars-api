"""Movement service: sector warping and sector info."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.player import Player
from app.models.port import Port, PortType
from app.models.sector import Sector, SectorWarp


async def get_sector_info(db: AsyncSession, sector_id: int) -> dict:
    """Get full sector info: details, warps, port summary, players present."""
    sector = await db.get(Sector, sector_id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    # Get warps out
    result = await db.execute(
        select(SectorWarp.to_sector_id).where(SectorWarp.from_sector_id == sector_id)
    )
    warp_targets = [row[0] for row in result.all()]

    # Get port if any (with eager loading)
    result = await db.execute(
        select(Port)
        .where(Port.sector_id == sector_id)
        .options(selectinload(Port.port_type))
    )
    port = result.scalar_one_or_none()
    port_info = None
    if port:
        port_info = {
            "id": port.id,
            "name": port.name,
            "port_type_id": port.port_type_id,
            "port_type_code": port.port_type.code if port.port_type else None,
            "port_type_name": port.port_type.name if port.port_type else None,
        }

    # Get players in sector
    result = await db.execute(
        select(Player.id, Player.username).where(Player.sector_id == sector_id)
    )
    players = [{"id": row[0], "username": row[1]} for row in result.all()]

    return {
        "id": sector.id,
        "name": sector.name,
        "is_fedspace": sector.is_fedspace,
        "nebula": sector.nebula,
        "beacon": sector.beacon,
        "warps": warp_targets,
        "port": port_info,
        "players": players,
    }


async def warp(db: AsyncSession, player: Player, target_sector_id: int) -> dict:
    """Move player to an adjacent sector via warp."""
    if player.turns_remaining <= 0:
        raise HTTPException(status_code=400, detail="No turns remaining")

    # Check adjacency
    result = await db.execute(
        select(SectorWarp).where(
            SectorWarp.from_sector_id == player.sector_id,
            SectorWarp.to_sector_id == target_sector_id,
        )
    )
    warp_link = result.scalar_one_or_none()
    if not warp_link:
        raise HTTPException(
            status_code=400,
            detail=f"No warp from sector {player.sector_id} to sector {target_sector_id}",
        )

    # Check target sector exists
    target = await db.get(Sector, target_sector_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target sector not found")

    # Turn cost: 3 if entering FedSpace from outside, else 1
    current_sector = await db.get(Sector, player.sector_id)
    entering_fedspace = target.is_fedspace and not current_sector.is_fedspace
    turn_cost = 3 if entering_fedspace else 1

    if player.turns_remaining < turn_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough turns (need {turn_cost}, have {player.turns_remaining})",
        )

    player.sector_id = target_sector_id
    player.turns_remaining -= turn_cost
    player.turns_used_today += turn_cost
    await db.commit()
    await db.refresh(player)

    return {
        "moved_to": target_sector_id,
        "turn_cost": turn_cost,
        "turns_remaining": player.turns_remaining,
    }
