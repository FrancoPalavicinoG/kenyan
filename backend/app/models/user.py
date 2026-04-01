from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .checkin import Checkin
    from .garmin_activity import GarminActivity
    from .garmin_daily_stats import GarminDailyStats
    from .garmin_hrv import GarminHrv
    from .garmin_sleep import GarminSleep
    from .goal import Goal


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    weight_kg: Mapped[Optional[float]]
    height_cm: Mapped[Optional[float]]
    birth_date: Mapped[Optional[date]]
    training_days_per_week: Mapped[Optional[int]]
    garmin_profile_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    checkins: Mapped[list["Checkin"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_stats: Mapped[list["GarminDailyStats"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sleep_records: Mapped[list["GarminSleep"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    hrv_records: Mapped[list["GarminHrv"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activities: Mapped[list["GarminActivity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, name={self.name!r})"
