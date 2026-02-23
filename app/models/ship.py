from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.commodity import Commodity
    from app.models.player import Player


class ShipType(Base):
    __tablename__ = "ship_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    holds: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    max_fighters: Mapped[int] = mapped_column(Integer, default=0)
    max_shields: Mapped[int] = mapped_column(Integer, default=0)
    offense: Mapped[int] = mapped_column(Integer, default=10)
    defense: Mapped[int] = mapped_column(Integer, default=10)


class Ship(Base):
    __tablename__ = "ships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ship_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ship_types.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), default="Unnamed")
    fighters: Mapped[int] = mapped_column(Integer, default=0)
    shields: Mapped[int] = mapped_column(Integer, default=0)
    hull: Mapped[int] = mapped_column(Integer, default=100)

    ship_type: Mapped[ShipType] = relationship("ShipType", lazy="noload")
    cargo: Mapped[list[ShipCargo]] = relationship(
        "ShipCargo", back_populates="ship", lazy="noload"
    )
    owner: Mapped[Player] = relationship("Player", back_populates="ship", uselist=False)


class ShipCargo(Base):
    __tablename__ = "ship_cargo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ship_id: Mapped[int] = mapped_column(Integer, ForeignKey("ships.id"), nullable=False)
    commodity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("commodities.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    ship: Mapped[Ship] = relationship("Ship", back_populates="cargo")
    commodity: Mapped[Commodity] = relationship("Commodity", lazy="noload")
