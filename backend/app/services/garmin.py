import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectTooManyRequestsError
from garth.exc import GarthHTTPError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import GarminActivity, GarminDailyStats, GarminHrv, GarminSleep
from app.schemas.sync import SyncResult

logger = logging.getLogger(__name__)

GARMIN_TOKENS_PATH = Path("~/.garminconnect").expanduser()
GARMIN_API_TIMEOUT_SECONDS = 20
GARMIN_BACKFILL_DAYS = 30


def get_garmin_client() -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(str(GARMIN_TOKENS_PATH))
        logger.info("Garmin: authenticated using cached tokens")
        return garmin
    except (FileNotFoundError, GarthHTTPError, GarminConnectConnectionError):
        logger.info("Garmin: no valid tokens found, logging in with credentials")
        garmin = Garmin(email=settings.GARMIN_EMAIL, password=settings.GARMIN_PASSWORD)
        garmin.login()
        garmin.garth.dump(str(GARMIN_TOKENS_PATH))
        logger.info("Garmin: tokens saved to %s", GARMIN_TOKENS_PATH)
        return garmin


def sync_daily_stats(
    db: Session, client: Garmin, user_id: int, target_date: date
) -> GarminDailyStats:
    date_str = target_date.isoformat()
    raw_stats = client.get_stats(date_str)

    record = (
        db.query(GarminDailyStats)
        .filter(GarminDailyStats.user_id == user_id, GarminDailyStats.date == target_date)
        .first()
    )
    if record is None:
        record = GarminDailyStats(user_id=user_id, date=target_date)

    record.total_steps = raw_stats.get("totalSteps")
    record.active_kcal = raw_stats.get("activeKilocalories")
    record.total_kcal = raw_stats.get("totalKilocalories")
    record.avg_stress_level = raw_stats.get("averageStressLevel")
    record.body_battery_high = raw_stats.get("bodyBatteryHighestValue")
    record.body_battery_low = raw_stats.get("bodyBatteryLowestValue")
    record.raw_payload = raw_stats

    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Synced daily stats for user %d date %s", user_id, date_str)
    return record


def sync_sleep(
    db: Session, client: Garmin, user_id: int, target_date: date
) -> GarminSleep:
    date_str = target_date.isoformat()
    raw_sleep = client.get_sleep_data(date_str)
    dto = raw_sleep.get("dailySleepDTO", {}) if isinstance(raw_sleep, dict) else {}

    record = (
        db.query(GarminSleep)
        .filter(GarminSleep.user_id == user_id, GarminSleep.date == target_date)
        .first()
    )
    if record is None:
        record = GarminSleep(user_id=user_id, date=target_date)

    record.sleep_seconds = dto.get("sleepTimeSeconds")
    record.deep_sleep_seconds = dto.get("deepSleepSeconds")
    record.light_sleep_seconds = dto.get("lightSleepSeconds")
    record.rem_sleep_seconds = dto.get("remSleepSeconds")
    record.awake_seconds = dto.get("awakeSleepSeconds")
    record.avg_respiration = dto.get("avgSleepRespirationValue")
    record.raw_payload = raw_sleep

    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Synced sleep for user %d date %s", user_id, date_str)
    return record


def sync_hrv(
    db: Session, client: Garmin, user_id: int, target_date: date
) -> GarminHrv:
    date_str = target_date.isoformat()
    raw_hrv = client.get_hrv_data(date_str)
    raw_readiness = client.get_training_readiness(date_str)

    hrv_summary = raw_hrv.get("hrvSummary", {}) if isinstance(raw_hrv, dict) else {}
    readiness = raw_readiness[0] if isinstance(raw_readiness, list) and raw_readiness else {}

    record = (
        db.query(GarminHrv)
        .filter(GarminHrv.user_id == user_id, GarminHrv.date == target_date)
        .first()
    )
    if record is None:
        record = GarminHrv(user_id=user_id, date=target_date)

    record.hrv_last_night_avg = hrv_summary.get("lastNightAvg")
    record.hrv_weekly_avg = hrv_summary.get("weeklyAvg")
    record.hrv_status = hrv_summary.get("status")
    record.readiness_score = readiness.get("score")
    record.readiness_level = readiness.get("level")
    record.readiness_feedback = readiness.get("feedbackLong")
    record.raw_payload = {"hrv": raw_hrv, "readiness": raw_readiness}

    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(
        "Synced HRV for user %d date %s: hrv=%s readiness=%s",
        user_id,
        date_str,
        hrv_summary.get("lastNightAvg"),
        readiness.get("score"),
    )
    return record


def sync_activities(
    db: Session, client: Garmin, user_id: int, limit: int = 20
) -> int:
    raw_activities = client.get_activities(0, limit)
    new_count = 0

    for activity in raw_activities:
        garmin_activity_id = activity.get("activityId")
        already_exists = (
            db.query(GarminActivity)
            .filter(GarminActivity.garmin_activity_id == garmin_activity_id)
            .first()
        )
        if already_exists:
            continue

        started_at_raw = activity.get("startTimeLocal")
        started_at = None
        if started_at_raw:
            try:
                started_at = datetime.strptime(started_at_raw, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning("Could not parse startTimeLocal %r for activity %s", started_at_raw, garmin_activity_id)

        new_activity = GarminActivity(
            user_id=user_id,
            garmin_activity_id=garmin_activity_id,
            name=activity.get("activityName"),
            type_key=activity.get("activityType", {}).get("typeKey"),
            started_at=started_at,
            duration_seconds=activity.get("duration"),
            distance_meters=activity.get("distance"),
            avg_hr=activity.get("averageHR"),
            max_hr=activity.get("maxHR"),
            training_effect_aerobic=activity.get("aerobicTrainingEffect"),
            training_effect_anaerobic=activity.get("anaerobicTrainingEffect"),
            raw_payload=activity,
        )
        db.add(new_activity)
        new_count += 1

    db.commit()
    logger.info("Synced %d new activities for user %d", new_count, user_id)
    return new_count


def run_daily_sync(db: Session, user_id: int) -> SyncResult:
    client = get_garmin_client()
    errors: list[str] = []
    synced_dates = 0

    for target_date in [date.today(), date.today() - timedelta(days=1)]:
        try:
            sync_daily_stats(db, client, user_id, target_date)
        except Exception as e:
            errors.append(f"stats {target_date}: {e}")

        try:
            sync_sleep(db, client, user_id, target_date)
        except Exception as e:
            errors.append(f"sleep {target_date}: {e}")

        try:
            sync_hrv(db, client, user_id, target_date)
        except Exception as e:
            errors.append(f"hrv {target_date}: {e}")

        synced_dates += 1

    new_activities = 0
    try:
        new_activities = sync_activities(db, client, user_id, limit=10)
    except Exception as e:
        errors.append(f"activities: {e}")

    return SyncResult(
        synced_dates=synced_dates,
        new_activities=new_activities,
        errors=errors,
    )


def run_backfill(db: Session, user_id: int, days: int = GARMIN_BACKFILL_DAYS) -> SyncResult:
    client = get_garmin_client()
    errors: list[str] = []
    synced_dates = 0

    for i in range(days):
        target_date = date.today() - timedelta(days=i)

        try:
            sync_daily_stats(db, client, user_id, target_date)
            sync_sleep(db, client, user_id, target_date)
            sync_hrv(db, client, user_id, target_date)
            synced_dates += 1
        except GarminConnectTooManyRequestsError as e:
            logger.warning("Rate limited at day %d, stopping backfill", i)
            errors.append(f"rate_limited at day {i}: {e}")
            break
        except Exception as e:
            errors.append(f"{target_date}: {e}")

        if i % 10 == 0:
            logger.info("Backfill progress: %d/%d days", i + 1, days)

    new_activities = 0
    try:
        new_activities = sync_activities(db, client, user_id, limit=50)
    except Exception as e:
        errors.append(f"activities: {e}")

    return SyncResult(
        synced_dates=synced_dates,
        new_activities=new_activities,
        errors=errors,
    )
