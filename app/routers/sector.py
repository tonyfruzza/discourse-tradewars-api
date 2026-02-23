from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_player
from app.db import get_db
from app.models.player import Player
from app.schemas.sector import PathfindResponse, SectorResponse, WarpRequest, WarpResponse
from app.services.movement import get_sector_info, warp
from app.services.pathfinding import find_path

router = APIRouter(prefix="/api", tags=["sector"])


@router.get("/sector", response_model=SectorResponse)
async def current_sector(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    return await get_sector_info(db, player.sector_id)


@router.get("/sector/{sector_id}", response_model=SectorResponse)
async def sector_info(
    sector_id: int,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    return await get_sector_info(db, sector_id)


@router.post("/sector/warp", response_model=WarpResponse)
async def warp_to_sector(
    body: WarpRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    return await warp(db, player, body.target_sector_id)


@router.get("/pathfind", response_model=PathfindResponse)
async def pathfind(
    src: int,  # renamed from 'from' which is a Python keyword
    to: int,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    return await find_path(db, src, to)
