from pydantic import BaseModel


class SyncResult(BaseModel):
    synced_dates: int
    new_activities: int
    errors: list[str] = []
