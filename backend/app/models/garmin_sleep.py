import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class GarminSleep(Base):
    __tablename__ = "garmin_sleep"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_sleep_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    sleep_seconds: Mapped[Optional[int]]
    deep_sleep_seconds: Mapped[Optional[int]]
    light_sleep_seconds: Mapped[Optional[int]]
    rem_sleep_seconds: Mapped[Optional[int]]
    awake_seconds: Mapped[Optional[int]]
    avg_respiration: Mapped[Optional[float]]
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship(back_populates="sleep_records")

    def __repr__(self) -> str:
        return f"GarminSleep(id={self.id}, user_id={self.user_id}, date={self.date})"
