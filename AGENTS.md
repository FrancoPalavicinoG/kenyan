# Kenyan — Agent Guidelines

Rules for AI coding agents working on the Kenyan codebase. Read CLAUDE.md first — this document adds agent-specific rules on top of it.

---

## What Kenyan Is

Kenyan is an AI coaching app that syncs Garmin biometric data and uses Claude to generate adaptive training plans. The codebase has two moving parts an agent must understand before touching anything:

1. **The data pipeline** — Python cron jobs that pull from Garmin Connect API and store normalized data + raw JSONB payloads in PostgreSQL.
2. **The agent layer** — FastAPI endpoints that assemble a structured prompt from the athlete's data and check-in responses, call Claude, parse the structured response, and return a workout to the frontend.

When in doubt about where logic belongs: routers are thin, services are thick, context builder is pure.

---

## Before Writing Any Code

1. **Read the relevant service file first.** Understand what already exists before adding anything.
2. **Check if a model already has the column you need** before creating a new one. Prefer `ALTER TABLE` via Alembic over new tables.
3. **Run the type checker before and after your change.** `mypy app/` for backend, `npm run type-check` for frontend.
4. **Never leave a migration half-done.** If you add a model column, generate and apply the migration in the same task.

---

## Backend Agent Rules

### Router pattern — always thin

```python
# CORRECT — the router does nothing except delegate
@router.get("/checkin/today", response_model=TodayCheckinResponse)
async def get_today_checkin_status(db: Session = Depends(get_db)):
    return await checkin_service.get_today_status(db)

# WRONG — router doing work
@router.get("/checkin/today")
async def get_today_checkin_status(db: Session = Depends(get_db)):
    today = date.today()
    metrics = db.query(DailyMetric).filter(DailyMetric.date == today).first()
    if not metrics:
        return {"status": "no_data"}
    return {"hrv": metrics.hrv_status, "readiness": metrics.training_readiness_score}
```

### Service pattern — one responsibility per method

```python
# CORRECT — small, named methods
class CheckinService:
    async def process_morning_checkin(self, db: Session, payload: CheckinCreate) -> CheckinResponse:
        todays_metrics = self._fetch_todays_garmin_metrics(db)
        athlete_patterns = self._fetch_recent_athlete_patterns(db)
        context_prompt = build_morning_checkin_context(todays_metrics, athlete_patterns, payload)
        agent_response = await generate_workout_for_checkin(context_prompt)
        saved_checkin = self._persist_checkin_and_workout(db, payload, agent_response)
        return CheckinResponse.model_validate(saved_checkin)

    def _fetch_todays_garmin_metrics(self, db: Session) -> Optional[DailyMetric]:
        return db.query(DailyMetric).filter(DailyMetric.date == date.today()).first()
```

### SQLAlchemy — never raw SQL, never session misuse

```python
# CORRECT — ORM query
def get_activities_in_date_range(
    db: Session,
    start_date: date,
    end_date: date,
) -> list[Activity]:
    return (
        db.query(Activity)
        .filter(Activity.activity_date >= start_date, Activity.activity_date <= end_date)
        .order_by(Activity.activity_date.desc())
        .all()
    )

# WRONG — raw SQL string
db.execute("SELECT * FROM activities WHERE date > '2024-01-01'")

# WRONG — creating session inside a service
db = SessionLocal()
result = db.query(...)
```

### Alembic — always generate migrations for model changes

```bash
# After changing any SQLAlchemy model:
alembic revision --autogenerate -m "describe_what_changed"
# Then verify the generated file looks correct before applying:
alembic upgrade head
```

Never modify the database schema by hand. Never call `Base.metadata.create_all()` outside tests.

### Garmin authentication — token store pattern (CRITICAL)

The `garminconnect` library uses `garth` under the hood for OAuth. **Never re-authenticate on every sync** — Garmin rate-limits repeated SSO logins aggressively (HTTP 429).

The correct pattern is token persistence:

```python
from pathlib import Path
from garminconnect import Garmin

GARMIN_TOKENSTORE = Path("~/.garminconnect").expanduser()

def initialize_garmin_client(email: str, password: str) -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(str(GARMIN_TOKENSTORE))
        return garmin
    except Exception:
        pass

    garmin = Garmin(email=email, password=password)
    garmin.login()
    GARMIN_TOKENSTORE.mkdir(parents=True, exist_ok=True)
    garmin.garth.dump(str(GARMIN_TOKENSTORE))
    return garmin
```

Rules:
- **Token store path is `~/.garminconnect`** — this is the library default. Do not use `~/.garth_tokens` or any other path.
- **Pass the path to `garmin.login(path)`** — do not call `garth.load()` separately. The `login()` method accepts the token directory directly.
- **Save tokens with `garmin.garth.dump(path)`** after the first credential login.
- **On subsequent calls**, `garmin.login(path)` loads and auto-refreshes the tokens without hitting SSO.
- The scheduler calls `initialize_garmin_client()` once at startup, not on every sync.

```python
# WRONG — causes 429 after a few runs
def sync(email: str, password: str) -> None:
    client = Garmin(email, password)
    client.login()  # hits SSO every time

# WRONG — wrong token path, wrong load API
client.garth.load("~/.garth_tokens")
```

---

### Garmin sync — raw payload first, normalize second

```python
# CORRECT — always save raw first
async def sync_daily_stats_for_date(db: Session, garmin_client: Garmin, sync_date: str) -> DailyMetric:
    raw_stats = await fetch_daily_stats_from_garmin(garmin_client, sync_date)  # has timeout
    raw_hrv = await fetch_hrv_data_from_garmin(garmin_client, sync_date)

    return upsert_daily_metric(db, date=sync_date, raw_stats=raw_stats, raw_hrv=raw_hrv)

def upsert_daily_metric(db: Session, *, date: str, raw_stats: dict, raw_hrv: dict) -> DailyMetric:
    existing = db.query(DailyMetric).filter(DailyMetric.date == date).first()
    metric = existing or DailyMetric(date=date)

    metric.garmin_raw_payload = {"stats": raw_stats, "hrv": raw_hrv}  # always persist raw
    metric.resting_heart_rate = raw_stats.get("restingHeartRate")
    metric.hrv_status = raw_hrv.get("hrvSummary", {}).get("status")
    metric.training_readiness_score = raw_stats.get("trainingReadinessScore")

    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric
```

### Context Builder — pure function, no side effects

The context builder must not query the database or call external services. It receives data objects and returns a string. This makes it testable and predictable.

```python
# CORRECT
def build_morning_checkin_context(
    todays_metrics: Optional[DailyMetric],
    recent_activities: list[Activity],
    user_responses: CheckinCreate,
    athlete_patterns: AthletePatterns,
) -> str:
    hrv_summary = _format_hrv_context(todays_metrics)
    activity_summary = _format_recent_activity_context(recent_activities)
    pattern_summary = _format_learned_patterns(athlete_patterns)
    checkin_summary = _format_user_checkin_responses(user_responses)

    return f"""
## Athlete Status — {date.today().isoformat()}

### Biometric Data (from Garmin)
{hrv_summary}

### Recent Training Load
{activity_summary}

### Learned Patterns
{pattern_summary}

### Today's Check-in
{checkin_summary}
"""

# WRONG — context builder with side effects
def build_context(db: Session, checkin_id: int) -> str:
    checkin = db.query(Checkin).get(checkin_id)  # DB query inside context builder
    ...
```

### Agent calls — parse and validate, never use raw text

```python
# CORRECT — parse Claude's response into a typed object
async def generate_workout_for_checkin(context_prompt: str) -> AgentWorkoutResponse:
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=COACH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context_prompt}],
    )
    raw_text = response.content[0].text
    return _parse_and_validate_agent_response(raw_text)

def _parse_and_validate_agent_response(raw_text: str) -> AgentWorkoutResponse:
    try:
        data = json.loads(raw_text)
        return AgentWorkoutResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.error("Agent response parse failed: %s | Raw snippet: %.200s", error, raw_text)
        raise AgentResponseParseError(str(error))

# WRONG — using raw text directly
response = anthropic_client.messages.create(...)
return {"message": response.content[0].text}  # no parsing, no validation
```

---

## Frontend Agent Rules

### TanStack Query for all server state

Never use `useState` + `useEffect` + raw `fetch` to load data from the API. Always use TanStack Query.

```tsx
// CORRECT
const { data: todayCheckin, isLoading, error } = useQuery({
  queryKey: ['checkin', 'today'],
  queryFn: () => api.getTodayCheckin(),
});

// WRONG
const [checkin, setCheckin] = useState(null);
useEffect(() => {
  fetch('/api/checkin/today').then(r => r.json()).then(setCheckin);
}, []);
```

Mutations also use TanStack Query:

```tsx
// CORRECT
const submitCheckin = useMutation({
  mutationFn: (payload: CheckinPayload) => api.submitMorningCheckin(payload),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['checkin', 'today'] });
    queryClient.invalidateQueries({ queryKey: ['workout', 'today'] });
  },
});
```

### API layer — all requests go through `src/api/`

Never call `fetch` directly in a component. All API calls go through typed functions in `src/api/`.

```tsx
// src/api/checkin.ts
export const checkinApi = {
  getTodayStatus: (): Promise<TodayCheckinResponse> =>
    apiClient.get('/checkin/today').then(r => r.data),

  submitMorningCheckin: (payload: CheckinCreate): Promise<CheckinResponse> =>
    apiClient.post('/checkin', payload).then(r => r.data),
};

// WRONG — fetch inside a component
const handleSubmit = async () => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/checkin`, {
    method: 'POST',
    body: JSON.stringify(formData),
  });
};
```

### TypeScript types mirror backend schemas

Types live in `frontend/src/types/`. When a backend Pydantic schema changes, update the corresponding TypeScript interface in the same commit.

```typescript
// frontend/src/types/checkin.ts — mirrors backend CheckinCreate schema
export interface CheckinCreate {
  energy_level: number;        // 1-5
  muscle_soreness: number;     // 1-5
  motivation: number;          // 1-5
  notes?: string;
}

export interface CheckinResponse {
  checkin_id: number;
  workout_of_the_day: WorkoutSummary;
  agent_message: string;
}
```

### Component structure

Pages go in `src/pages/`. Reusable UI goes in `src/components/`. Page-specific sub-components stay co-located with the page file.

```
src/pages/
├── CheckIn/
│   ├── CheckInPage.tsx        # page entry point + TanStack Query
│   ├── CheckInForm.tsx        # form component
│   └── WorkoutResult.tsx      # result display after submission
├── Dashboard/
│   ├── DashboardPage.tsx
│   ├── MetricsGrid.tsx
│   └── TrainingLoadChart.tsx
└── Plan/
    ├── PlanPage.tsx
    └── WeekCalendar.tsx
```

### Environment variables

```tsx
// CORRECT — always use env var
const apiUrl = import.meta.env.VITE_API_URL;

// WRONG — hardcoded URL
const apiUrl = 'http://localhost:8000';
```

All frontend env vars are prefixed with `VITE_`. They live in `frontend/.env.local` (not committed).

---

## What Not To Do (Common Agent Mistakes)

- **Don't add logic to routers.** Move it to a service.
- **Don't query the DB inside the context builder.** Pass data in as arguments.
- **Don't use Claude's raw response text in the app.** Always parse into a typed schema.
- **Don't call Garmin or Anthropic without a timeout.** Use `asyncio.wait_for`.
- **Don't create new tables without a migration.** Run `alembic revision --autogenerate`.
- **Don't use `useState` + `useEffect` + `fetch` for server data.** Use TanStack Query.
- **Don't hardcode API URLs in components.** Use `import.meta.env.VITE_API_URL`.
- **Don't push with type errors.** Run `mypy` and `npm run type-check` first.
- **Don't skip the raw Garmin payload save.** Always persist to `garmin_raw_payload` (JSONB) before normalizing.
- **Don't invent new patterns.** Look at what's already in `services/` before writing anything new.
