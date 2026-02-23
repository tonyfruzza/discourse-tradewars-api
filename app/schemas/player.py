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
    experience: int
    turns_remaining: int
    turns_used_today: int
    ship: "ShipResponse | None" = None
    created_at: datetime
    updated_at: datetime


class ShipResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    ship_type_name: str | None = None
    holds: int = 0
    fighters: int
    shields: int
    hull: int
    cargo: list["CargoResponse"] = []
    cargo_used: int = 0


class CargoResponse(BaseModel):
    model_config = {"from_attributes": True}

    commodity_id: int
    commodity_code: str | None = None
    commodity_name: str | None = None
    quantity: int


class PlayerPreferencesRequest(BaseModel):
    digest_opt_in: bool | None = None
