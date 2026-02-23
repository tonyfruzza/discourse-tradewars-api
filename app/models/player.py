from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discourse_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=20000)
    sector_id: Mapped[int] = mapped_column(Integer, default=1)
    ship_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ships.id", use_alter=True), nullable=True
    )
    alignment: Mapped[int] = mapped_column(Integer, default=0)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    turns_remaining: Mapped[int] = mapped_column(Integer, default=300)
    turns_used_today: Mapped[int] = mapped_column(Integer, default=0)
    digest_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    ship: Mapped["Ship"] = relationship("Ship", back_populates="owner", lazy="noload")
