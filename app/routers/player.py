from fastapi import APIRouter, Depends

from app.auth import get_current_player
from app.models.player import Player
from app.schemas.player import PlayerResponse

router = APIRouter(prefix="/api", tags=["player"])


@router.get("/me", response_model=PlayerResponse)
async def get_me(player: Player = Depends(get_current_player)):
    return player
