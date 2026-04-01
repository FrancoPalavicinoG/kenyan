from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TodayMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    readiness_score: Optional[int] = None
    readiness_level: Optional[str] = None
    hrv_last_night_avg: Optional[int] = None
    hrv_status: Optional[str] = None
    sleep_seconds: Optional[int] = None
    avg_respiration: Optional[float] = None
    avg_stress_level: Optional[int] = None
    total_steps: Optional[int] = None
    has_checkin_today: bool = False
