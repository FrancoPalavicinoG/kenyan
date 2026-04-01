from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import Checkin, GarminDailyStats, GarminHrv, GarminSleep
from app.schemas.metrics import TodayMetrics


def get_today_metrics(db: Session, user_id: int) -> TodayMetrics:
    today = date.today()
    yesterday = today - timedelta(days=1)

    hrv = (
        db.query(GarminHrv)
        .filter(GarminHrv.user_id == user_id, GarminHrv.date == today)
        .first()
    ) or (
        db.query(GarminHrv)
        .filter(GarminHrv.user_id == user_id, GarminHrv.date == yesterday)
        .first()
    )

    sleep = (
        db.query(GarminSleep)
        .filter(GarminSleep.user_id == user_id, GarminSleep.date == today)
        .first()
    ) or (
        db.query(GarminSleep)
        .filter(GarminSleep.user_id == user_id, GarminSleep.date == yesterday)
        .first()
    )

    stats = (
        db.query(GarminDailyStats)
        .filter(GarminDailyStats.user_id == user_id, GarminDailyStats.date == today)
        .first()
    ) or (
        db.query(GarminDailyStats)
        .filter(GarminDailyStats.user_id == user_id, GarminDailyStats.date == yesterday)
        .first()
    )

    has_checkin_today = (
        db.query(Checkin)
        .filter(Checkin.user_id == user_id, Checkin.date == today)
        .first()
    ) is not None

    return TodayMetrics(
        date=today,
        readiness_score=hrv.readiness_score if hrv else None,
        readiness_level=hrv.readiness_level if hrv else None,
        hrv_last_night_avg=hrv.hrv_last_night_avg if hrv else None,
        hrv_status=hrv.hrv_status if hrv else None,
        sleep_seconds=sleep.sleep_seconds if sleep else None,
        avg_respiration=sleep.avg_respiration if sleep else None,
        avg_stress_level=stats.avg_stress_level if stats else None,
        total_steps=stats.total_steps if stats else None,
        active_kcal=stats.active_kcal if stats else None,
        total_kcal=stats.total_kcal if stats else None,
        has_checkin_today=has_checkin_today,
    )
