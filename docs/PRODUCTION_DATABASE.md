# PULSE AI — Production Database Guide

This document describes the database setup, schema initialization, and migration strategy for **PULSE AI**.

---

## 1. Supported Database Systems

PULSE AI supports dual database configurations via Async SQLAlchemy 2.0:

### A. Local Development & Demo (`SQLite`)
- **ConnectionString:** `sqlite+aiosqlite:///./pulse.db`
- **Driver:** `aiosqlite`
- **Use Case:** Zero-config local development, unit testing, and instant demo execution.
- **Data File:** `backend/pulse.db` (preserved across runs).

### B. Production Deployment (`PostgreSQL`)
- **ConnectionString:** `postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>`
- **Driver:** `asyncpg`
- **Use Case:** Production cloud deployments (e.g. Render PostgreSQL, AWS RDS, Supabase, Neon).

---

## 2. Dynamic Connection Normalization

The database initialization in [database.py](file:///d:/PULSE/backend/app/database.py) automatically inspects `DATABASE_URL` from the environment and injects the appropriate async driver:
```python
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
```

---

## 3. Schema Initialization & Migration Process

### Automatic Schema Creation
On application startup ([main.py](file:///d:/PULSE/backend/app/main.py)), FastAPI executes async metadata initialization:
```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```
This creates all required tables, foreign keys, indexes, and relationships automatically on fresh PostgreSQL instances without requiring manual DDL execution.

### Preserved Database Schema Models
The ORM schema includes:
1. `User` & `UserPreferences`: User credentials, working hours (start/end window), task buffer defaults.
2. `OAuthAccount`: Secure storage for Google OAuth access tokens, refresh tokens, and expiration timestamps.
3. `TaskItem` & `TaskDependency`: Tasks, deadlines, priorities, status, effort duration, and parent-child dependencies.
4. `CalendarEvent`: Fixed commitments, start/end datetimes, and sync metadata.
5. `DailyPlan`, `PlanItem`, & `PlanVersion`: Daily attention schedules, XAI scheduling rationale, plan versions, and change diff logs.
6. `EmailMessage` & `NotificationItem`: Gmail and mobile notification message records with AI classification tags.
7. `DocumentItem` & `ExtractedInformation`: Uploaded circulars/documents and extracted obligations.
8. `AIDecision` & `AuditLog`: Audit trails and risk classification records for AI actions.

---

## 4. Environment Variables for Deployment

For production deployments (e.g. Render, Railway, Fly.io):

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://pulse_user:secure_password@postgres-host:5432/pulse_db
```

In production mode (`ENVIRONMENT=production`), automatic demo dataset seeding is disabled, and the system operates strictly on live user data.
