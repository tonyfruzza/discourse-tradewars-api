from datetime import datetime

from pydantic import BaseModel


class PlayerResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    discourse_user_id: int
    username: str
    credits: int
    sector_id: int
    alignment: int
    turns_remaining: int
    created_at: datetime
    updated_at: datetime
