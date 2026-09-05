# PULSE AI — Personal Unified Life Scheduling & Execution Agent

> **Everything important in your digital life. One intelligent plan for your day.**

---

## 🌟 Overview & Core Value

**PULSE AI** is an AI-powered **Attention-to-Execution Engine** built for modern professionals facing information overload across disparate digital channels (email, calendar invites, circulars, documents, mobile alerts, and informal notes).

Rather than acting as a passive summarizer or generic chatbot, PULSE AI actively understands incoming obligations, filters noise, estimates task effort, respects fixed calendar commitments, builds an optimized daily schedule within user focus hours, and dynamically replans the day when interruptions, delays, or new obligations arrive.

---

## 🎯 Problem & Solution

### The Problem
- **Attention Fragmentation:** Important obligations are scattered across Gmail, Google Calendar, PDFs, and chat messages.
- **Manual Overhead:** Estimating effort, checking calendar conflicts, and building daily task lists takes significant manual effort.
- **Fragile Schedules:** A single delayed task or unexpected meeting renders a static to-do list useless for the rest of the day.

### The Solution
- **Unified Ingestion:** Consolidates incoming items and classifies them into `ACTION_REQUIRED`, `INFORMATION_ONLY`, `PROMOTIONAL`, or `IRRELEVANT`.
- **Attention Budget Planner:** Calculates daily focus hours (work window minus fixed calendar commitments) and schedules tasks around meetings with zero overlap.
- **Explainable AI (XAI):** Provides transparent natural language rationale for every scheduled task slot.
- **Dynamic Replanning:** Automatically recalculates the day schedule upon task completion, deletion, or reported delay, keeping plan version history (`Plan v1 -> Plan v2`).

---

## 🛠️ Technology Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, React, Tailwind CSS (Dark Glassmorphism Design System).
- **Backend:** Python 3.13, FastAPI, Pydantic v2, Async SQLAlchemy 2.0.
- **Database:** Dual Driver Architecture — Async SQLite (`aiosqlite`) for zero-setup local dev; PostgreSQL (`asyncpg`) for production.
- **AI Engine:** Extensible LLM Provider Layer (OpenAI `gpt-4o-mini`, Google Gemini `gemini-1.5-flash`) with structured Pydantic schema validation and fallback rule heuristics.
- **Timezone Engine:** UTC normalization module (`app/utils/datetime_utils.py`) enforcing consistent UTC datetimes across deadlines, events, and plan slots.

---

## 🏗️ System Architecture

```
[ Gmail API / Mobile Alerts / Document PDFs / NLI Input ]
                           │
                           ▼
          [ FastAPI Ingestion & Classification Layer ]
                           │
                           ▼
        [ Structured Action & Subtask Extractor ]
                           │
                           ▼
      [ Attention Budget & Focus Capacity Solver ]
                           │
                           ▼
     [ Topological Schedule & Conflict Avoidance Engine ]
                           │
                           ▼
     [ Explainable AI (XAI) Daily Plan & Timeline View ]
                           │
                           ▼
   [ Dynamic Replanning Engine (Plan Versioning v1 -> v2) ]
```

---

## 📊 Database Configuration

PULSE AI uses dynamic database URL driver mapping ([docs/PRODUCTION_DATABASE.md](file:///d:/PULSE/docs/PRODUCTION_DATABASE.md)):

- **Local Development:** `DATABASE_URL=sqlite+aiosqlite:///./pulse.db`
- **Production Cloud:** `DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<dbname>`

Tables created automatically on launch: `User`, `UserPreferences`, `OAuthAccount`, `TaskItem`, `TaskDependency`, `CalendarEvent`, `DailyPlan`, `PlanItem`, `PlanVersion`, `EmailMessage`, `DocumentItem`, `AIDecision`, `AuditLog`, `MobileDevice`.

---

## 🔌 Google Integrations (OAuth / Gmail / Calendar)

PULSE AI features end-to-end support for Google OAuth 2.0 PKCE, Gmail API message ingestion, and Google Calendar event sync.

- **Truthful Status Reporting:** When `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are unconfigured in environment, the system displays `FALLBACK / UNSET` in System Settings without faking connection state.
- **Live Readiness:** Supplying valid Google Cloud credentials enables full consent, token refresh (`get_valid_google_token`), and live email/calendar ingestion.

---

## 💻 Local Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend running at `http://localhost:8000`. API Documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend running at `http://localhost:3000`.

---

## 🔑 Environment Variables Template

Create `backend/.env`:
```env
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./pulse.db
SECRET_KEY=development_secret_key_change_in_production

# AI Engine Credentials
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
AI_API_KEY=your_openai_api_key

# Optional Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google
```

---

## 🚀 Production Deployment Configuration

- **Docker Compose:** Run `docker-compose up --build` for containerized PostgreSQL + FastAPI + Next.js setup.
- **Render Backend:** Configured via [render.yaml](file:///d:/PULSE/render.yaml).
- **Vercel Frontend:** Configured via [vercel.json](file:///d:/PULSE/vercel.json).
- **Production Mode:** Setting `ENVIRONMENT=production` automatically disables demo dataset seeding and operates strictly on live user data.

---

## 🎬 Core User Demo Journey

1. **Dashboard (`/`)**: View current day attention budget, planned workload %, and interactive timeline.
2. **Unified Task Matrix (`/tasks`)**: Click **"+ Create Task"** to add a task with priority, category, and deadline. Notice automatic replan execution.
3. **AI Plan View (`/plan`)**: Inspect scheduled time slots and hover to read **Explainable AI (XAI)** scheduling rationale.
4. **Natural Language Bar**: Type *"I couldn't finish my preparation today, please replan my day"* to trigger dynamic replanning and generate **Plan v2**.
5. **System Settings (`/settings`)**: View environment status and truthful integration badges.

---

## 🛡️ Security & Data Privacy

- **Secret Protection:** Zero API keys or client secrets committed to Git (`.env` git-ignored).
- **CSRF & PKCE:** Dynamic `state` token validation on OAuth authorization.
- **Privacy Export:** GDPR-compliant JSON data export endpoint (`GET /api/v1/privacy/export`).

---

## 🧪 Testing & Verification

Run the backend test suite:
```bash
cd backend
python -m pytest
```
**Test Results:** `9/9 passed` (100% pass rate).
**Type Checking:** `npx tsc --noEmit` passed with 0 errors.

---

## 🏆 Razorpay AI Builder Buildathon Submission Notes

- Audit Report: [FINAL_BUILDATHON_AUDIT.md](file:///d:/PULSE/FINAL_BUILDATHON_AUDIT.md)
- Deployment Audit: [FINAL_DEPLOYMENT_AUDIT.md](file:///d:/PULSE/FINAL_DEPLOYMENT_AUDIT.md)
- Submission Readiness Report: [FINAL_SUBMISSION_READINESS.md](file:///d:/PULSE/FINAL_SUBMISSION_READINESS.md)
