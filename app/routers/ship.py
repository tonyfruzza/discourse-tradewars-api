from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_player
from app.db import get_db
from app.models.player import Player
from app.models.ship import Ship, ShipCargo

router = APIRouter(prefix="/api", tags=["ship"])


@router.get("/ship")
async def get_ship(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    if not player.ship_id:
        raise HTTPException(status_code=404, detail="No ship assigned")

    result = await db.execute(
        select(Ship)
        .where(Ship.id == player.ship_id)
        .options(
            selectinload(Ship.ship_type),
            selectinload(Ship.cargo).selectinload(ShipCargo.commodity),
        )
    )
    ship = result.scalar_one_or_none()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")

    cargo_items = []
    cargo_used = 0
    for c in ship.cargo:
        cargo_used += c.quantity
        cargo_items.append({
            "commodity_id": c.commodity_id,
            "commodity_code": c.commodity.code if c.commodity else None,
            "commodity_name": c.commodity.name if c.commodity else None,
            "quantity": c.quantity,
        })

    return {
        "id": ship.id,
        "name": ship.name,
        "ship_type_name": ship.ship_type.name if ship.ship_type else None,
        "holds": ship.ship_type.holds if ship.ship_type else 0,
        "fighters": ship.fighters,
        "shields": ship.shields,
        "hull": ship.hull,
        "cargo": cargo_items,
        "cargo_used": cargo_used,
    }
