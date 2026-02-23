"""Player enrollment and management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.player import Player
from app.models.ship import Ship, ShipType


async def auto_enroll(
    db: AsyncSession, discourse_user_id: int, username: str
) -> Player:
    """Create a new player. If the galaxy exists, assign a starting ship."""
    ship_id = None

    # Try to create a starting ship (Merchant Cruiser, id=2) if ship types exist
    ship_type = (await db.execute(
        select(ShipType).where(ShipType.id == 2)
    )).scalar_one_or_none()

    if ship_type:
        ship = Ship(
            ship_type_id=ship_type.id,
            name=f"{username}'s Merchant Cruiser",
            fighters=0,
            shields=0,
        )
        db.add(ship)
        await db.flush()
        ship_id = ship.id

    player = Player(
        discourse_user_id=discourse_user_id,
        username=username,
        credits=20000,
        sector_id=1,
        ship_id=ship_id,
        alignment=0,
        experience=0,
        turns_remaining=settings.TURNS_PER_DAY,
        turns_used_today=0,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player
