from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import DecodeError, ExpiredSignatureError, decode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db import get_db
from app.models.player import Player
from app.models.ship import Ship, ShipCargo
from app.services.player_service import auto_enroll

bearer_scheme = HTTPBearer()


async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Player:
    token = credentials.credentials
    try:
        payload = decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    discourse_user_id = payload.get("discourse_user_id")
    username = payload.get("username", "unknown")
    if discourse_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    result = await db.execute(
        select(Player)
        .where(Player.discourse_user_id == discourse_user_id)
        .options(
            selectinload(Player.ship)
            .selectinload(Ship.ship_type),
            selectinload(Player.ship)
            .selectinload(Ship.cargo)
            .selectinload(ShipCargo.commodity),
        )
    )
    player = result.scalar_one_or_none()

    if player is None:
        player = await auto_enroll(db, discourse_user_id, username)

    return player


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except (ExpiredSignatureError, DecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not payload.get("admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

    return payload
