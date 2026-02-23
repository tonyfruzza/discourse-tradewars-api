from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PortType(Base):
    __tablename__ = "port_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    ore_mode: Mapped[str] = mapped_column(String(4), nullable=False)
    org_mode: Mapped[str] = mapped_column(String(4), nullable=False)
    equ_mode: Mapped[str] = mapped_column(String(4), nullable=False)


class Port(Base):
    __tablename__ = "ports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sectors.id"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    port_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("port_types.id"), nullable=False
    )
    cash: Mapped[int] = mapped_column(Integer, default=100000)

    sector: Mapped["Sector"] = relationship("Sector", back_populates="port")
    port_type: Mapped["PortType"] = relationship("PortType", lazy="noload")
    stock: Mapped[list["PortStock"]] = relationship(
        "PortStock", back_populates="port", lazy="noload"
    )


class PortStock(Base):
    __tablename__ = "port_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    port_id: Mapped[int] = mapped_column(Integer, ForeignKey("ports.id"), nullable=False)
    commodity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("commodities.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    max_quantity: Mapped[int] = mapped_column(Integer, default=1000)
    mode: Mapped[str] = mapped_column(String(4), nullable=False)

    port: Mapped["Port"] = relationship("Port", back_populates="stock")
    commodity: Mapped["Commodity"] = relationship("Commodity", lazy="noload")
