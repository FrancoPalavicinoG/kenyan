import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class GarminDailyStats(Base):
    __tablename__ = "garmin_daily_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    total_steps: Mapped[Optional[int]]
    active_kcal: Mapped[Optional[float]]
    total_kcal: Mapped[Optional[float]]
    avg_stress_level: Mapped[Optional[int]]
    body_battery_high: Mapped[Optional[int]]
    body_battery_low: Mapped[Optional[int]]
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship(back_populates="daily_stats")

    def __repr__(self) -> str:
        return f"GarminDailyStats(id={self.id}, user_id={self.user_id}, date={self.date})"
