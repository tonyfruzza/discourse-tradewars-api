from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.services.tick import run_tick

router = APIRouter(tags=["tick"])


async def verify_tick_api_key(request: Request):
    """Verify the tick API key from the X-Tick-Api-Key header."""
    api_key = request.headers.get("X-Tick-Api-Key")
    if not api_key or api_key != settings.TICK_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid tick API key")


@router.post("/api/tick", dependencies=[Depends(verify_tick_api_key)])
async def execute_tick(db: AsyncSession = Depends(get_db)):
    result = await run_tick(db)
    return result
