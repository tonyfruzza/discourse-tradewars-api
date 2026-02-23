from pydantic import BaseModel


class PortResponse(BaseModel):
    id: int
    name: str
    sector_id: int
    port_type_id: int
    port_type_code: str | None
    port_type_name: str | None
    cash: int
    stock: list["StockItem"]


class StockItem(BaseModel):
    commodity_id: int
    commodity_code: str
    commodity_name: str
    mode: str
    quantity: int
    max_quantity: int
    price: int


class TradeRequest(BaseModel):
    commodity_id: int
    action: str  # "buy" or "sell"
    quantity: int


class TradeResponse(BaseModel):
    action: str
    commodity: str
    quantity: int
    price_per_unit: int
    total: int
    credits_remaining: int
    turns_remaining: int
