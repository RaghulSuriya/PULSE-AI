# PULSE AI — Final Submission Readiness Report
**Razorpay AI Builder Buildathon 2026 Submission**
*Date: September 5, 2026*

---

## A. Product Overview
- **Name:** PULSE AI (Personal Unified Life Scheduling & Execution Agent)
- **Tagline:** Everything important in your digital life. One intelligent plan for your day.
- **Repository:** Full-stack application containing Next.js 14 frontend, FastAPI backend, Async SQLAlchemy ORM, and Kotlin Android companion.

---

## B. Core Problem
Modern professionals face attention fragmentation across disparate channels (emails, calendar invites, circulars, instant messages, and informal notes). Information overload causes missed obligations, poor time estimation, manual scheduling overhead, and chaotic days when unexpected delays occur.

---

## C. Core Solution
PULSE AI acts as an AI Attention-to-Execution Engine. It automatically consolidates obligations across channels, filters promotional noise, estimates task effort, respects fixed calendar commitments, builds an explainable daily schedule within user focus hours, and dynamically replans the day when interruptions or delays occur.

---

## D. AI Architecture
- **Provider Layer:** Extensible multi-provider abstraction ([base.py](file:///d:/PULSE/backend/app/services/ai_engine/base.py)) supporting OpenAI (`gpt-4o-mini`), Google Gemini (`gemini-1.5-flash`), and rule-based heuristic fallback parsers.
- **Structured Outputs:** Enforces strict Pydantic JSON schema validation across all extractions.
- **Resilience:** Built-in 15-second timeout protection, exponential backoff retries (up to 3 attempts), and fallback parser guarantee 100% system availability even if LLM APIs fail.
- **Explainable AI (XAI):** Generates transparent natural language rationale for every scheduled task slot.

---

## E. Technical Architecture
- **Frontend:** Next.js 14 (App Router), TypeScript, React, Tailwind CSS (Dark Glassmorphism aesthetic).
- **Backend:** FastAPI, Python 3.13, Pydantic v2, Async SQLAlchemy 2.0.
- **Database:** Dual driver support — SQLite (`aiosqlite`) for zero-config local dev; PostgreSQL (`asyncpg`) for production.
- **Timezone Engine:** Timezone-aware UTC normalization engine ([datetime_utils.py](file:///d:/PULSE/backend/app/utils/datetime_utils.py)) enforcing consistent UTC comparison across deadlines, events, and slots.

---

## F. Frontend / Backend Integration Status
Fully connected via REST API client ([api.ts](file:///d:/PULSE/frontend/src/lib/api.ts)). All 14 primary frontend routes execute live backend requests with zero mock state bypasses.

---

## G. Database
- **Development:** Local SQLite database (`pulse.db`) preserved intact.
- **Production:** PostgreSQL supported via `DATABASE_URL` auto-driver conversion. Fully documented in [docs/PRODUCTION_DATABASE.md](file:///d:/PULSE/docs/PRODUCTION_DATABASE.md).

---

## H. AI Provider Status
`LIVE` when `AI_API_KEY` is provided; seamlessly defaults to `RULE HEURISTICS` when unconfigured without crashing.

---

## I. Gmail Integration Status
`PARTIAL / REQUIRES CREDENTIALS`. Ingestion, deduplication, and classification pipeline verified; requires Google OAuth client secrets for live email ingestion. Displays `FALLBACK / UNSET` truthfully when unconfigured.

---

## J. Calendar Integration Status
`PARTIAL / REQUIRES CREDENTIALS`. Calendar event sync and planner zero-overlap logic verified; requires Google OAuth client secrets for live primary calendar ingestion.

---

## K. Planner Engine
`LIVE`. Calculates total daily focus capacity (work window minus fixed commitments), prioritizes tasks by urgency/deadline using `MAX_UTC_DATETIME`, allocates buffer times, and flags overload warnings.

---

## L. Dynamic Replanning Engine
`LIVE`. Automatically recalculates day plan upon task creation, update, deletion, completion, or user delay. Tracks plan versions (`Plan v1 -> Plan v2`) with diff summaries.

---

## M. Document Intelligence
`LIVE`. Accepts PDF/text circulars, extracts requirements, identifies deadlines, and generates subtask graphs.

---

## N. Natural Language Interface (NLI)
`LIVE`. Parses user conversational input into structured intents (`CREATE_TASK`, `ADD_CALENDAR_EVENT`, `REPLAN_DAY`).

---

## O. Security & Privacy
- **Secrets:** Zero API keys or credentials committed to Git. `.env` is git-ignored.
- **OAuth Security:** PKCE and state parameter CSRF validation active.
- **Privacy Export:** GDPR-compliant JSON data export endpoint active.

---

## P. Deployment
- **Docker Compose:** [docker-compose.yml](file:///d:/PULSE/docker-compose.yml) (Postgres + Backend + Frontend).
- **Backend Cloud:** [render.yaml](file:///d:/PULSE/render.yaml) blueprint for Render deployment.
- **Frontend Cloud:** [vercel.json](file:///d:/PULSE/vercel.json) for Vercel deployment.

---

## Q. Known Limitations
1. **Google OAuth Production Registration:** Live Google sync requires registering Client ID/Secret in Google Cloud Console.
2. **Android APK Compilation:** Kotlin source available in `/android-companion`; requires Gradle build.

---

## R. Demo Instructions (Core Evaluation Flow)
1. Open Frontend at `http://localhost:3000` (Backend running at `http://localhost:8000`).
2. Navigate to **Unified Task Matrix (`/tasks`)** and click **"+ Create Task"**.
3. Create a task titled *"Prepare Razorpay Buildathon Submission"* with a 60-min duration and deadline.
4. Navigate to **My Plan (`/plan`)** to inspect the allocated time slot and Explainable AI (XAI) rationale.
5. In the Quick Command bar at the top, enter: *"I couldn't finish my preparation today, please replan my day"*.
6. Watch the planner execute dynamic replanning and generate **Plan v2**.
7. Navigate to **System Settings (`/settings`)** to inspect environment health and channel status.

---

## S. Exact Truthful Feature Status Matrix

| Feature / Subsystem | Status Category | Verification Notes |
| :--- | :--- | :--- |
| **Task Management (Create/Edit/Delete)** | `LIVE` | 100% verified via API and UI |
| **Attention Budget & Planner Engine** | `LIVE` | 100% verified via Pytest suite |
| **Timezone UTC Datetime Normalization** | `LIVE` | 100% verified via Pytest suite |
| **Dynamic Replanning & Versioning** | `LIVE` | 100% verified via Pytest suite |
| **Natural Language Input (NLI) Parser** | `LIVE` | 100% verified via Pytest suite |
| **Document Processing & Subtasks** | `LIVE` | 100% verified via file upload |
| **Privacy Data Export** | `LIVE` | 100% verified via API endpoint |
| **OpenAI / Gemini LLM Integration** | `LIVE` | Verified with live `gpt-4o-mini` API key |
| **Google OAuth 2.0 Flow** | `PARTIAL / REQUIRES CREDENTIALS` | Code complete; awaiting Google Client secrets |
| **Gmail API Live Sync** | `PARTIAL / REQUIRES CREDENTIALS` | Pipeline active; awaiting OAuth access token |
| **Google Calendar API Live Sync** | `PARTIAL / REQUIRES CREDENTIALS` | Planner active; awaiting OAuth access token |
| **Local SQLite Development DB** | `DEVELOPMENT ONLY` | `pulse.db` preserved for local testing |
| **Demo Dataset Auto-Seeder** | `DEVELOPMENT ONLY` | Disabled automatically when `ENVIRONMENT=production` |
| **Android Companion App** | `DEVELOPMENT ONLY` | Kotlin source provided in `/android-companion` |
| **Autonomous Payments** | `NOT IMPLEMENTED` | Omitted by design |
