from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.port import Port


class Sector(Base):
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Uncharted Space")
    beacon: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_fedspace: Mapped[bool] = mapped_column(Boolean, default=False)
    nebula: Mapped[bool] = mapped_column(Boolean, default=False)

    port: Mapped[Port] = relationship(
        "Port", back_populates="sector", uselist=False, lazy="noload"
    )
    warps_out: Mapped[list[SectorWarp]] = relationship(
        "SectorWarp", foreign_keys="SectorWarp.from_sector_id",
        back_populates="from_sector", lazy="noload"
    )


class SectorWarp(Base):
    __tablename__ = "sector_warps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_sector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sectors.id"), index=True, nullable=False
    )
    to_sector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sectors.id"), index=True, nullable=False
    )

    from_sector: Mapped[Sector] = relationship(
        "Sector", foreign_keys=[from_sector_id], back_populates="warps_out"
    )

    __table_args__ = (
        UniqueConstraint("from_sector_id", "to_sector_id", name="uq_sector_warp"),
    )
