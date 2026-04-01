from datetime import date
from typing import Optional

from app.models import GarminActivity, GarminDailyStats, GarminHrv, GarminSleep
from app.schemas.checkin import CheckinCreate


def build_checkin_context(
    today: date,
    checkin: CheckinCreate,
    hrv_today: Optional[GarminHrv],
    sleep_today: Optional[GarminSleep],
    stats_today: Optional[GarminDailyStats],
    recent_activities: list[GarminActivity],
    hrv_30d_avg: Optional[float],
    readiness_7d_avg: Optional[float],
    sleep_7d_avg_seconds: Optional[float],
) -> str:
    readiness_score = hrv_today.readiness_score if hrv_today else "Sin datos"
    readiness_level = hrv_today.readiness_level if hrv_today else "Sin datos"
    hrv_last_night = hrv_today.hrv_last_night_avg if hrv_today else "Sin datos"
    hrv_status = hrv_today.hrv_status if hrv_today else "Sin datos"
    avg_stress = stats_today.avg_stress_level if stats_today else "Sin datos"

    sleep_hours = sleep_today.sleep_seconds / 3600 if sleep_today and sleep_today.sleep_seconds else 0.0
    sleep_7d_avg_hours = sleep_7d_avg_seconds / 3600 if sleep_7d_avg_seconds else 0.0

    hrv_30d_str = f"{hrv_30d_avg:.0f} ms" if hrv_30d_avg is not None else "Sin datos"
    readiness_7d_str = f"{readiness_7d_avg:.0f}" if readiness_7d_avg is not None else "Sin datos"

    if recent_activities:
        activity_lines = []
        for activity in recent_activities:
            duration_min = int(activity.duration_seconds / 60) if activity.duration_seconds else 0
            days_ago = (today - activity.started_at.date()).days if activity.started_at else "?"
            name = activity.name or "Actividad"
            type_key = activity.type_key or "desconocido"
            avg_hr = activity.avg_hr or "Sin datos"
            activity_lines.append(
                f"- {name} ({type_key}): {duration_min}min, FC {avg_hr}bpm — {days_ago} días atrás"
            )
        activities_text = "\n".join(activity_lines)
    else:
        activities_text = "Sin actividades recientes registradas"

    return f"""
## Check-in matutino — {today.isoformat()}

### Métricas del reloj (Garmin) — hoy
- Training Readiness: {readiness_score} ({readiness_level})
- HRV anoche: {hrv_last_night} ms
- Estado HRV: {hrv_status}
- Sueño: {sleep_hours:.1f}h
- Estrés promedio ayer: {avg_stress}

### Promedios históricos (últimos 30 días)
- HRV promedio 30d: {hrv_30d_str}
- Readiness promedio 7d: {readiness_7d_str}
- Sueño promedio 7d: {sleep_7d_avg_hours:.1f}h

### Últimas actividades
{activities_text}

### Sensaciones hoy (check-in del atleta)
- Energía: {checkin.energy_level}/5
- Dolor muscular: {checkin.soreness}/5
- Sueño percibido: {checkin.perceived_sleep_hours}h
- Sensación general: {checkin.general_feeling}/5
"""
