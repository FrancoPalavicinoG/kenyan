import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Checkin, GarminActivity, GarminDailyStats, GarminHrv, GarminSleep
from app.schemas.checkin import CheckinCreate, CheckinResponse
from app.services.agent import generate_daily_insight
from app.services.context import build_checkin_context

logger = logging.getLogger(__name__)


def get_today_checkin(db: Session, user_id: int) -> Checkin | None:
    return (
        db.query(Checkin)
        .filter(Checkin.user_id == user_id, Checkin.date == date.today())
        .first()
    )


def _fetch_garmin_data(db: Session, user_id: int) -> tuple:
    today = date.today()
    yesterday = today - timedelta(days=1)

    hrv_today = (
        db.query(GarminHrv)
        .filter(GarminHrv.user_id == user_id, GarminHrv.date == today)
        .first()
    ) or (
        db.query(GarminHrv)
        .filter(GarminHrv.user_id == user_id, GarminHrv.date == yesterday)
        .first()
    )

    sleep_today = (
        db.query(GarminSleep)
        .filter(GarminSleep.user_id == user_id, GarminSleep.date == today)
        .first()
    ) or (
        db.query(GarminSleep)
        .filter(GarminSleep.user_id == user_id, GarminSleep.date == yesterday)
        .first()
    )

    stats_today = (
        db.query(GarminDailyStats)
        .filter(GarminDailyStats.user_id == user_id, GarminDailyStats.date == today)
        .first()
    ) or (
        db.query(GarminDailyStats)
        .filter(GarminDailyStats.user_id == user_id, GarminDailyStats.date == yesterday)
        .first()
    )

    recent_activities = (
        db.query(GarminActivity)
        .filter(GarminActivity.user_id == user_id)
        .order_by(GarminActivity.started_at.desc())
        .limit(5)
        .all()
    )

    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    hrv_30d_avg = db.query(
        func.avg(GarminHrv.hrv_last_night_avg)
    ).filter(
        GarminHrv.user_id == user_id,
        GarminHrv.date >= thirty_days_ago,
        GarminHrv.hrv_last_night_avg.isnot(None),
    ).scalar()

    readiness_7d_avg = db.query(
        func.avg(GarminHrv.readiness_score)
    ).filter(
        GarminHrv.user_id == user_id,
        GarminHrv.date >= seven_days_ago,
        GarminHrv.readiness_score.isnot(None),
    ).scalar()

    sleep_7d_avg_seconds = db.query(
        func.avg(GarminSleep.sleep_seconds)
    ).filter(
        GarminSleep.user_id == user_id,
        GarminSleep.date >= seven_days_ago,
        GarminSleep.sleep_seconds.isnot(None),
    ).scalar()

    return (
        hrv_today,
        sleep_today,
        stats_today,
        recent_activities,
        hrv_30d_avg,
        readiness_7d_avg,
        sleep_7d_avg_seconds,
    )


async def create_checkin(
    db: Session, user_id: int, payload: CheckinCreate
) -> CheckinResponse:
    existing = get_today_checkin(db, user_id)
    if existing:
        logger.info("Checkin already exists for user %d today", user_id)
        return CheckinResponse.model_validate(existing)

    (
        hrv_today,
        sleep_today,
        stats_today,
        recent_activities,
        hrv_30d_avg,
        readiness_7d_avg,
        sleep_7d_avg_seconds,
    ) = _fetch_garmin_data(db, user_id)

    logger.info(
        "Garmin data fetched for checkin: hrv=%s readiness=%s sleep=%s activities=%d",
        hrv_today.hrv_last_night_avg if hrv_today else None,
        hrv_today.readiness_score if hrv_today else None,
        sleep_today.sleep_seconds if sleep_today else None,
        len(recent_activities),
    )

    context_prompt = build_checkin_context(
        today=date.today(),
        checkin=payload,
        hrv_today=hrv_today,
        sleep_today=sleep_today,
        stats_today=stats_today,
        recent_activities=recent_activities,
        hrv_30d_avg=hrv_30d_avg,
        readiness_7d_avg=readiness_7d_avg,
        sleep_7d_avg_seconds=sleep_7d_avg_seconds,
    )

    logger.info("Context prompt built, length=%d chars", len(context_prompt))

    insight = await generate_daily_insight(context_prompt)

    logger.info(
        "Agent insight generated: sugerencia=%s tono=%s",
        insight.sugerencia_dia,
        insight.tono,
    )

    checkin = Checkin(
        user_id=user_id,
        date=date.today(),
        energy_level=payload.energy_level,
        soreness=payload.soreness,
        perceived_sleep_hours=payload.perceived_sleep_hours,
        general_feeling=payload.general_feeling,
        workout_generated=insight.model_dump(),
        agent_message=insight.resumen,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    logger.info("Checkin saved: id=%d user=%d", checkin.id, user_id)

    return CheckinResponse.model_validate(checkin)
