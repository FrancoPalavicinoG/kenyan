import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class GarminHrv(Base):
    __tablename__ = "garmin_hrv"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_hrv_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    hrv_last_night_avg: Mapped[Optional[int]]
    hrv_weekly_avg: Mapped[Optional[int]]
    hrv_status: Mapped[Optional[str]] = mapped_column(String(20))
    readiness_score: Mapped[Optional[int]]
    readiness_level: Mapped[Optional[str]] = mapped_column(String(20))
    readiness_feedback: Mapped[Optional[str]]
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship(back_populates="hrv_records")

    def __repr__(self) -> str:
        return (
            f"GarminHrv(id={self.id}, user_id={self.user_id}, date={self.date}, "
            f"hrv_status={self.hrv_status!r}, readiness_score={self.readiness_score})"
        )
