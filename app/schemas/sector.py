from pydantic import BaseModel


class SectorResponse(BaseModel):
    id: int
    name: str
    is_fedspace: bool
    nebula: bool
    beacon: str | None
    warps: list[int]
    port: "PortSummary | None" = None
    players: list["PlayerSummary"] = []


class PortSummary(BaseModel):
    id: int
    name: str
    port_type_id: int
    port_type_code: str | None
    port_type_name: str | None


class PlayerSummary(BaseModel):
    id: int
    username: str


class WarpRequest(BaseModel):
    target_sector_id: int


class WarpResponse(BaseModel):
    moved_to: int
    turn_cost: int
    turns_remaining: int


class PathfindResponse(BaseModel):
    path: list[int]
    hops: int
    error: str | None = None
