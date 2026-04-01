import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_checkin_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    energy_level: Mapped[Optional[int]]
    soreness: Mapped[Optional[int]]
    perceived_sleep_hours: Mapped[Optional[float]]
    general_feeling: Mapped[Optional[int]]
    workout_generated: Mapped[Optional[dict]] = mapped_column(JSONB)
    agent_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="checkins")

    def __repr__(self) -> str:
        return f"Checkin(id={self.id}, user_id={self.user_id}, date={self.date})"
