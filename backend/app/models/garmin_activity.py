from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class GarminActivity(Base):
    __tablename__ = "garmin_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    garmin_activity_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(String)
    type_key: Mapped[Optional[str]] = mapped_column(String, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(index=True)
    duration_seconds: Mapped[Optional[float]]
    distance_meters: Mapped[Optional[float]]
    avg_hr: Mapped[Optional[int]]
    max_hr: Mapped[Optional[int]]
    training_effect_aerobic: Mapped[Optional[float]]
    training_effect_anaerobic: Mapped[Optional[float]]
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship(back_populates="activities")

    def __repr__(self) -> str:
        return (
            f"GarminActivity(id={self.id}, user_id={self.user_id}, "
            f"garmin_activity_id={self.garmin_activity_id}, type_key={self.type_key!r})"
        )
