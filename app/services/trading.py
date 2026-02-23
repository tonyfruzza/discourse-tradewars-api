"""Trading service: port info and buy/sell transactions."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.commodity import Commodity
from app.models.player import Player
from app.models.port import Port, PortStock
from app.models.ship import Ship, ShipCargo
from app.models.trade_log import TradeLog


def calculate_price(base_price: int, volatility: int, quantity: int, max_quantity: int) -> int:
    """Calculate current price based on supply.

    Price formula: base_price * (1 + volatility/100 * (1 - quantity/max_quantity))
    Low stock = high price, high stock = low price.
    """
    if max_quantity == 0:
        return base_price
    supply_factor = 1 - (quantity / max_quantity)
    price = base_price * (1 + (volatility / 100) * supply_factor)
    return max(1, int(round(price)))


async def get_port_info(db: AsyncSession, port_id: int) -> dict:
    """Get full port info with stock levels and current prices."""
    result = await db.execute(
        select(Port)
        .where(Port.id == port_id)
        .options(
            selectinload(Port.port_type),
            selectinload(Port.stock).selectinload(PortStock.commodity),
        )
        .execution_options(populate_existing=True)
    )
    port = result.scalar_one_or_none()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")

    stock_items = []
    for ps in port.stock:
        commodity = ps.commodity
        price = calculate_price(
            commodity.base_price, commodity.volatility, ps.quantity, ps.max_quantity
        )
        stock_items.append({
            "commodity_id": commodity.id,
            "commodity_code": commodity.code,
            "commodity_name": commodity.name,
            "mode": ps.mode,
            "quantity": ps.quantity,
            "max_quantity": ps.max_quantity,
            "price": price,
        })

    return {
        "id": port.id,
        "name": port.name,
        "sector_id": port.sector_id,
        "port_type_id": port.port_type_id,
        "port_type_code": port.port_type.code if port.port_type else None,
        "port_type_name": port.port_type.name if port.port_type else None,
        "cash": port.cash,
        "stock": stock_items,
    }


async def get_port_in_sector(db: AsyncSession, sector_id: int) -> Port | None:
    """Find the port in a given sector, if any."""
    result = await db.execute(select(Port).where(Port.sector_id == sector_id))
    return result.scalar_one_or_none()


async def _load_player_ship(db: AsyncSession, player: Player) -> Ship | None:
    """Eagerly load player's ship with cargo and type."""
    if not player.ship_id:
        return None
    result = await db.execute(
        select(Ship)
        .where(Ship.id == player.ship_id)
        .options(
            selectinload(Ship.ship_type),
            selectinload(Ship.cargo).selectinload(ShipCargo.commodity),
        )
    )
    return result.scalar_one_or_none()


def _get_cargo_total(ship: Ship) -> int:
    """Calculate total cargo currently in ship holds."""
    return sum(c.quantity for c in ship.cargo)


async def trade(
    db: AsyncSession,
    player: Player,
    commodity_id: int,
    action: str,
    quantity: int,
) -> dict:
    """Execute a buy or sell transaction at the port in the player's current sector."""
    if action not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="Action must be 'buy' or 'sell'")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    if player.turns_remaining <= 0:
        raise HTTPException(status_code=400, detail="No turns remaining")

    # Find port in current sector with eager loading
    result = await db.execute(
        select(Port)
        .where(Port.sector_id == player.sector_id)
        .options(
            selectinload(Port.stock).selectinload(PortStock.commodity),
        )
        .execution_options(populate_existing=True)
    )
    port = result.scalar_one_or_none()
    if not port:
        raise HTTPException(status_code=400, detail="No port in current sector")

    # Find the port stock for this commodity
    stock = None
    for ps in port.stock:
        if ps.commodity_id == commodity_id:
            stock = ps
            break
    if not stock:
        raise HTTPException(status_code=400, detail="Commodity not available at this port")

    commodity = stock.commodity
    price = calculate_price(
        commodity.base_price, commodity.volatility, stock.quantity, stock.max_quantity
    )

    # Load ship eagerly
    ship = await _load_player_ship(db, player)

    if action == "buy":
        if stock.mode != "sell":
            raise HTTPException(
                status_code=400,
                detail=f"Port does not sell {commodity.name} (port buys it instead)",
            )
        if stock.quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Port only has {stock.quantity} {commodity.name} available",
            )
        total_cost = price * quantity
        if player.credits < total_cost:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough credits (need {total_cost}, have {player.credits})",
            )
        if not ship:
            raise HTTPException(status_code=400, detail="No ship assigned")
        current_cargo = _get_cargo_total(ship)
        ship_holds = ship.ship_type.holds if ship.ship_type else 0
        if current_cargo + quantity > ship_holds:
            available = ship_holds - current_cargo
            raise HTTPException(
                status_code=400,
                detail=f"Not enough holds (available: {available}, need: {quantity})",
            )

        stock.quantity -= quantity
        player.credits -= total_cost
        port.cash += total_cost
        await _add_cargo(db, ship, commodity_id, quantity)

    else:
        if stock.mode != "buy":
            raise HTTPException(
                status_code=400,
                detail=f"Port does not buy {commodity.name} (port sells it instead)",
            )
        if not ship:
            raise HTTPException(status_code=400, detail="No ship assigned")
        cargo_item = None
        for c in ship.cargo:
            if c.commodity_id == commodity_id:
                cargo_item = c
                break
        if not cargo_item or cargo_item.quantity < quantity:
            have = cargo_item.quantity if cargo_item else 0
            raise HTTPException(
                status_code=400,
                detail=f"Not enough cargo (have {have}, trying to sell {quantity})",
            )
        total_revenue = price * quantity
        if port.cash < total_revenue:
            raise HTTPException(status_code=400, detail="Port doesn't have enough credits")

        stock.quantity += quantity
        player.credits += total_revenue
        port.cash -= total_revenue
        cargo_item.quantity -= quantity
        if cargo_item.quantity == 0:
            await db.delete(cargo_item)

    player.turns_remaining -= 1
    player.turns_used_today += 1

    db.add(TradeLog(
        player_id=player.id,
        port_id=port.id,
        commodity_id=commodity_id,
        action=action,
        quantity=quantity,
        price_per_unit=price,
        total=price * quantity,
    ))

    await db.commit()

    return {
        "action": action,
        "commodity": commodity.name,
        "quantity": quantity,
        "price_per_unit": price,
        "total": price * quantity,
        "credits_remaining": player.credits,
        "turns_remaining": player.turns_remaining,
    }


async def _add_cargo(
    db: AsyncSession, ship: Ship, commodity_id: int, quantity: int
) -> None:
    """Add cargo to ship, creating or updating the ShipCargo record."""
    for c in ship.cargo:
        if c.commodity_id == commodity_id:
            c.quantity += quantity
            return
    cargo = ShipCargo(ship_id=ship.id, commodity_id=commodity_id, quantity=quantity)
    db.add(cargo)
