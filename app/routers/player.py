from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_player
from app.db import get_db
from app.models.player import Player
from app.schemas.player import PlayerPreferencesRequest, PlayerResponse

router = APIRouter(prefix="/api", tags=["player"])


@router.get("/me", response_model=PlayerResponse)
async def get_me(player: Player = Depends(get_current_player)):
    ship = player.ship
    ship_data = None
    if ship:
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
        ship_data = {
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

    return PlayerResponse(
        id=player.id,
        discourse_user_id=player.discourse_user_id,
        username=player.username,
        credits=player.credits,
        sector_id=player.sector_id,
        alignment=player.alignment,
        experience=player.experience,
        turns_remaining=player.turns_remaining,
        turns_used_today=player.turns_used_today,
        ship=ship_data,
        created_at=player.created_at,
        updated_at=player.updated_at,
    )


@router.put("/me/preferences")
async def update_preferences(
    body: PlayerPreferencesRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    if body.digest_opt_in is not None:
        player.digest_opt_in = body.digest_opt_in
    await db.commit()
    return {"status": "ok"}
