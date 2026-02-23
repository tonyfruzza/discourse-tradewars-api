"""Daily tick service: regenerate turns, restock ports, gather digest data."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.player import Player
from app.models.port import PortStock


async def run_tick(db: AsyncSession) -> dict:
    """Execute the daily tick.

    1. Regenerate player turns
    2. Reset turns_used_today
    3. Restock ports (10% of max per tick, capped)
    4. Gather digest summary data
    """
    # 1. Regenerate turns
    await db.execute(
        update(Player).values(
            turns_remaining=settings.TURNS_PER_DAY,
            turns_used_today=0,
        )
    )

    # 2. Restock ports — each port stock gets +10% of max, capped at max
    stocks = (await db.execute(select(PortStock))).scalars().all()
    restocked = 0
    for stock in stocks:
        regen = int(stock.max_quantity * 0.10)
        if stock.mode == "sell":
            # Port sells: restock toward max
            new_qty = min(stock.quantity + regen, stock.max_quantity)
        else:
            # Port buys: drain toward 0
            new_qty = max(stock.quantity - regen, 0)
        if new_qty != stock.quantity:
            stock.quantity = new_qty
            restocked += 1

    await db.commit()

    # 3. Gather digest data
    player_count = (await db.execute(
        select(Player.id)
    )).all()

    top_players = (await db.execute(
        select(Player.username, Player.credits)
        .order_by(Player.credits.desc())
        .limit(5)
    )).all()

    opted_in = (await db.execute(
        select(Player.discourse_user_id, Player.username)
        .where(Player.digest_opt_in.is_(True))
    )).all()

    return {
        "players_updated": len(player_count),
        "ports_restocked": restocked,
        "turns_per_day": settings.TURNS_PER_DAY,
        "top_players": [
            {"username": row[0], "credits": row[1]} for row in top_players
        ],
        "opted_in_users": [
            {"discourse_user_id": row[0], "username": row[1]} for row in opted_in
        ],
    }
