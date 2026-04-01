from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CheckinCreate(BaseModel):
    energy_level: int = Field(..., ge=1, le=5)
    soreness: int = Field(..., ge=1, le=5)
    perceived_sleep_hours: float = Field(..., ge=0, le=24)
    general_feeling: int = Field(..., ge=1, le=5)


class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    energy_level: int
    soreness: int
    perceived_sleep_hours: float
    general_feeling: int
    workout_generated: Optional[dict] = None
    agent_message: Optional[str] = None
    created_at: datetime
