from pydantic import BaseModel


class BigBangRequest(BaseModel):
    galaxy_size: int = 500
    seed: int | None = None


class BigBangResponse(BaseModel):
    sectors: int
    fedspace_sectors: int
    ports: int
    warps: int
    ship_types: int
    commodities: int
    port_types: int


class StatsResponse(BaseModel):
    total_sectors: int
    total_ports: int
    total_players: int
    total_warps: int
    galaxy_age_days: int | None = None


class RankingEntry(BaseModel):
    rank: int
    username: str
    credits: int
    alignment: int
    experience: int
