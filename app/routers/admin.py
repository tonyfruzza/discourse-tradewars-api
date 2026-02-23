from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_player, require_admin
from app.bigbang.generator import bigbang
from app.db import get_db
from app.models.player import Player
from app.models.port import Port
from app.models.sector import Sector, SectorWarp
from app.schemas.admin import BigBangRequest, BigBangResponse, RankingEntry, StatsResponse

router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/admin/bigbang", response_model=BigBangResponse)
async def trigger_bigbang(
    body: BigBangRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await bigbang(db, galaxy_size=body.galaxy_size, seed=body.seed)
    return result


@router.get("/rankings", response_model=list[RankingEntry])
async def get_rankings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Player).order_by(Player.credits.desc()).limit(50)
    )
    players = result.scalars().all()
    return [
        RankingEntry(
            rank=i + 1,
            username=p.username,
            credits=p.credits,
            alignment=p.alignment,
            experience=p.experience,
        )
        for i, p in enumerate(players)
    ]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    sectors = (await db.execute(select(func.count(Sector.id)))).scalar() or 0
    ports = (await db.execute(select(func.count(Port.id)))).scalar() or 0
    players = (await db.execute(select(func.count(Player.id)))).scalar() or 0
    warps = (await db.execute(select(func.count(SectorWarp.id)))).scalar() or 0

    return StatsResponse(
        total_sectors=sectors,
        total_ports=ports,
        total_players=players,
        total_warps=warps,
    )
