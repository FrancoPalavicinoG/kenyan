# Kenyan — Claude Code Guidelines

**FastAPI + SQLAlchemy + PostgreSQL backend · Vite + React frontend · Anthropic SDK agent layer**

These rules apply to all code in the `kenyan/` repository. Read this before touching any file.

---

## Project Overview

Kenyan is an AI-powered athletic training coach that syncs data from Garmin wearables and uses a Claude-powered agent to generate personalized, adaptive training plans. The agent adapts daily based on biometric data (HRV, sleep, Training Readiness) and user check-ins.

**Monorepo structure:**
```
kenyan/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── main.py
│   │   ├── models/       # SQLAlchemy models (one file per domain)
│   │   ├── routers/      # FastAPI routers (thin — logic lives in services)
│   │   ├── services/     # All business logic lives here
│   │   │   ├── garmin.py       # Garmin Connect sync
│   │   │   ├── agent.py        # Claude API calls
│   │   │   ├── context.py      # Context Builder (assembles prompts)
│   │   │   └── scheduler.py    # APScheduler cron jobs
│   │   ├── schemas/      # Pydantic request/response models
│   │   └── db.py         # SQLAlchemy session
│   ├── alembic/          # Migrations
│   └── requirements.txt
├── frontend/         # Vite + React + TypeScript
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/          # TanStack Query hooks
│   │   └── types/        # TypeScript interfaces mirroring backend schemas
│   └── vite.config.ts
└── docs/             # Architecture and integration docs
```

---

## Code Rules (ALL files)

- **Verbose, descriptive names.** `garmin_daily_metrics_for_date` beats `get_data`. `training_readiness_score` beats `score`.
- **Small, declarative functions.** If a function needs a comment to explain what it does, rename it or split it.
- **No comments.** Express intent through naming and structure. The only acceptable comments are `# TODO:` with a reason.
- **No magic numbers.** Extract constants with descriptive names: `GARMIN_SYNC_TIMEOUT_SECONDS = 10`, not `timeout=10`.
- **Write code in English.** User-facing copy (UI labels, error messages shown to users) may be in Spanish.
- **DRY.** If you write it twice, extract it. No exceptions.
- **Prefer extending existing models over new tables.** A new table must be justified by a clear domain boundary.

---

## Backend Rules (FastAPI + SQLAlchemy)

### Architecture pattern: Router → Service → Repository

Routers are thin. They validate input (via Pydantic schemas), call one service method, and return the result. No business logic in routers.

```python
# CORRECT — thin router
@router.post("/checkin", response_model=CheckinResponse)
async def create_checkin(
    payload: CheckinCreate,
    db: Session = Depends(get_db),
):
    return await checkin_service.process_morning_checkin(db, payload)

# WRONG — logic in router
@router.post("/checkin")
async def create_checkin(payload: CheckinCreate, db: Session = Depends(get_db)):
    metrics = db.query(DailyMetric).filter(...).first()
    hrv = metrics.hrv_status
    prompt = f"HRV is {hrv}..."
    response = anthropic_client.messages.create(...)
    # ... 40 more lines
```

Services own all business logic. Keep service methods focused — one responsibility per method.

### SQLAlchemy models

All models live in `backend/app/models/`. One file per domain: `daily_metric.py`, `activity.py`, `training_plan.py`, `checkin.py`, `goal.py`.

```python
# CORRECT model pattern
class DailyMetric(Base):
    __tablename__ = "daily_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hrv_status: Mapped[Optional[str]] = mapped_column(String(50))
    resting_heart_rate: Mapped[Optional[int]] = mapped_column(Integer)
    training_readiness_score: Mapped[Optional[int]] = mapped_column(Integer)
    sleep_score: Mapped[Optional[int]] = mapped_column(Integer)
    garmin_raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)  # raw Garmin response
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
```

- Always use `Mapped[...]` typed column declarations (SQLAlchemy 2.0 style).
- Add `index=True` to every column used in WHERE or ORDER BY.
- Use `JSONB` for Garmin raw API payloads — do not try to normalize everything upfront.
- Every table gets `created_at`. Update-heavy tables get `updated_at` with `onupdate=func.now()`.

### Alembic migrations

Every schema change goes through Alembic. Never alter the database manually.

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "add_sleep_score_to_daily_metrics"

# Apply
alembic upgrade head
```

Never use `Base.metadata.create_all()` outside of initial dev setup. Production schema lives in migrations only.

### Pydantic schemas

All request bodies and responses use Pydantic v2 schemas in `backend/app/schemas/`. Schemas mirror what the API sends/receives — they are not the same as SQLAlchemy models.

```python
# CORRECT — separate schema from model
class CheckinCreate(BaseModel):
    energy_level: int = Field(ge=1, le=5)
    muscle_soreness: int = Field(ge=1, le=5)
    motivation: int = Field(ge=1, le=5)
    notes: Optional[str] = None

class CheckinResponse(BaseModel):
    checkin_id: int
    workout_of_the_day: WorkoutSummary
    agent_message: str

    model_config = ConfigDict(from_attributes=True)
```

### Database sessions

Use the `get_db` dependency. Never instantiate sessions manually inside route handlers or services.

```python
# CORRECT
def get_training_readiness_for_date(db: Session, target_date: date) -> Optional[DailyMetric]:
    return db.query(DailyMetric).filter(DailyMetric.date == target_date).first()

# WRONG — never do this inside a service
db = SessionLocal()
try:
    ...
finally:
    db.close()
```

### External integrations (CRITICAL)

Every call to Garmin Connect or the Anthropic API must have a timeout. No exceptions.

```python
# CORRECT — Garmin call with timeout
async def fetch_daily_stats_from_garmin(client: Garmin, target_date: str) -> dict:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(client.get_stats, target_date),
            timeout=GARMIN_API_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Garmin stats fetch timed out for date %s", target_date)
        raise GarminSyncTimeoutError(target_date)

# WRONG — no timeout
def fetch_stats(client, date):
    return client.get_stats(date)
```

Constants for timeouts live in `backend/app/config.py`:
```python
GARMIN_API_TIMEOUT_SECONDS = 15
ANTHROPIC_API_TIMEOUT_SECONDS = 30
GARMIN_SYNC_MAX_RETRIES = 3
```

### Logging

Use Python's standard `logging` module with a shared logger. Never use `print()`.

```python
import logging
logger = logging.getLogger(__name__)

# CORRECT
logger.info("Garmin sync completed for date %s: %d metrics saved", sync_date, saved_count)
logger.error("Claude API call failed for checkin %d: %s", checkin_id, str(error))

# WRONG
print(f"synced {date}")
```

---

## Agent Layer Rules (Anthropic SDK)

The agent layer lives in `backend/app/services/agent.py` and `backend/app/services/context.py`.

### Never call the Anthropic API directly from a router or model

All Claude calls go through `agent.py`. Routers call services, services call `agent.py`.

### Context Builder is the heart of the system

`context.py` assembles the structured prompt sent to Claude. It must be deterministic and testable — given the same inputs, it must produce the same prompt. Keep it as a pure function that takes data objects and returns a string.

```python
# CORRECT — pure function, easy to test
def build_morning_checkin_context(
    daily_metrics: DailyMetric,
    recent_activities: list[Activity],
    user_responses: CheckinCreate,
    historical_patterns: AthletePatterns,
) -> str:
    ...
    return assembled_prompt

# WRONG — mixing DB queries with prompt assembly
def build_context(db: Session, checkin: CheckinCreate) -> str:
    metrics = db.query(DailyMetric)...  # side effect inside context builder
```

### Structured prompts

Always separate system prompt from user prompt. The system prompt defines the agent's role and constraints. The user prompt contains the dynamic context.

```python
COACH_SYSTEM_PROMPT = """
You are Kenyan, an elite athletic training coach specializing in endurance sports.
You have deep expertise in the Norwegian double-threshold training method, VO2max development,
and periodization for events like HYROX and trail races.

You always respond in the same language the athlete uses.
You base every recommendation on the biometric data and subjective feedback provided.
You never recommend training that contradicts the athlete's current recovery status.
When Training Readiness is below 40, always reduce intensity and volume.

Respond with a JSON object matching this schema: {workout_of_the_day: {...}, message: string, nutrition_note: string}
"""
```

```python
# CORRECT — calling the SDK
async def generate_workout_for_checkin(context_prompt: str) -> AgentWorkoutResponse:
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=COACH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context_prompt}],
    )
    return parse_agent_response(response.content[0].text)
```

### Parse and validate Claude's response

Never use Claude's raw text directly in the app. Always parse and validate it.

```python
# CORRECT — parse and validate
def parse_agent_workout_response(raw_text: str) -> AgentWorkoutResponse:
    try:
        data = json.loads(raw_text)
        return AgentWorkoutResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.error("Failed to parse Claude response: %s | Raw: %s", error, raw_text[:200])
        raise AgentResponseParseError(str(error))
```

---

## Garmin Sync Rules

- The daily sync cron runs at **06:00 local time** via APScheduler.
- Always save the raw Garmin API response in `garmin_raw_payload` (JSONB) before normalizing. This lets us re-process historical data if we add new fields later.
- Use backfill logic for first-run: fetch the last **90 days** of data.
- Never delete existing daily metric rows on re-sync — use `INSERT ... ON CONFLICT DO UPDATE` via SQLAlchemy's `merge()`.
- Log every sync with date, duration, and count of records saved.

---

## Dev Environment

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --port 8000

# Type check
mypy app/

# Run migrations
alembic upgrade head

# Frontend
cd frontend
npm install
npm run dev       # Vite dev server on :5173
npm run type-check
npm run build
```

PostgreSQL runs locally via Docker:
```bash
docker compose up -d postgres
```

Environment variables go in `backend/.env` (never committed):
```
DATABASE_URL=postgresql://kenyan:kenyan@localhost:5432/kenyan_dev
ANTHROPIC_API_KEY=sk-ant-...
GARMIN_EMAIL=...
GARMIN_PASSWORD=...
```

---

## Type Safety (BLOCKING — Never Skip)

### Backend

Run `mypy app/` before committing any Python file. Fix all errors before pushing.

```bash
# Type check
mypy app/

# Common errors to watch for:
# - Optional[X] returned where X expected → add None guard
# - Missing return type on service functions → always annotate
```

### Frontend

Run `npm run type-check` before committing any TypeScript file. Fix all errors before pushing.

```bash
npm run type-check
```

TypeScript interfaces in `frontend/src/types/` must mirror backend Pydantic schema fields exactly. When you change a backend schema, update the frontend type in the same commit.

---

## Commit Checklist

Before committing backend code:
- [ ] `mypy app/` exits with 0 errors
- [ ] All new service methods have return type annotations
- [ ] All external calls (Garmin, Anthropic) have timeouts
- [ ] New tables have an Alembic migration
- [ ] No `print()` statements — use `logger`
- [ ] No business logic in routers

Before committing frontend code:
- [ ] `npm run type-check` exits with 0 errors
- [ ] `npm run build` succeeds
- [ ] No hardcoded API URLs — use `import.meta.env.VITE_API_URL`
- [ ] TanStack Query used for all server state (no raw `fetch` in components)

---

## Documentation Guidelines

- Feature plans go in `docs/featureplans/` when explicitly requested.
- Integration docs go in `backend/app/services/{name}/README.md`.
- **Do not create markdown files unless explicitly asked.**
- This file is a living document — update it after every correction or new pattern established.
