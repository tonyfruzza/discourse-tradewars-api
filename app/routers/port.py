from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_player
from app.db import get_db
from app.models.player import Player
from app.schemas.port import PortResponse, TradeRequest, TradeResponse
from app.services.trading import get_port_in_sector, get_port_info, trade

router = APIRouter(prefix="/api", tags=["port"])


@router.get("/port", response_model=PortResponse)
async def current_port(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    port = await get_port_in_sector(db, player.sector_id)
    if not port:
        raise HTTPException(status_code=404, detail="No port in current sector")
    return await get_port_info(db, port.id)


@router.post("/port/trade", response_model=TradeResponse)
async def trade_at_port(
    body: TradeRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    return await trade(db, player, body.commodity_id, body.action, body.quantity)
