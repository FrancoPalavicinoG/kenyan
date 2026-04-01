from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    name: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    birth_date: Optional[date] = None
    training_days_per_week: Optional[int] = None
    garmin_profile_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    birth_date: Optional[date] = None
    training_days_per_week: Optional[int] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    birth_date: Optional[date] = None
    training_days_per_week: Optional[int] = None
    garmin_profile_id: Optional[int] = None
    created_at: datetime
