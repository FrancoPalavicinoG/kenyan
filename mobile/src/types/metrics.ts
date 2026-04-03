export interface TodayMetrics {
  date: string
  readiness_score: number | null
  readiness_level: string | null
  hrv_last_night_avg: number | null
  hrv_status: string | null
  sleep_seconds: number | null
  avg_respiration: number | null
  avg_stress_level: number | null
  total_steps: number | null
  active_kcal: number | null
  total_kcal: number | null
  has_checkin_today: boolean
}
