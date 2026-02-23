from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)
    volatility: Mapped[int] = mapped_column(Integer, default=20)
    illegal: Mapped[bool] = mapped_column(Boolean, default=False)
