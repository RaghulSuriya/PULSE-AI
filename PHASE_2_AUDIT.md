# PULSE AI — PHASE 2 ENGINEERING AUDIT REPORT

**Date:** 2026-09-05  
**System:** Personal Unified Life Scheduling & Execution Agent (PULSE AI)  
**Audit Purpose:** Comprehensive inspection of core backend, frontend, OAuth flows, Gmail, Google Calendar, AI Provider abstractions, and security model prior to Phase 2 integration live enablement.

---

## 1. Executive Summary

The PULSE AI repository possesses a functional full-stack architecture built on FastAPI (async SQLAlchemy 2.0 with SQLite/PostgreSQL) and Next.js 14 App Router. All 4 core backend pytest suites pass, `compileall` reports 0 errors, and Next.js TypeScript check reports 0 errors.

However, several Phase 2 live integration pathways are currently **PARTIAL** or rely on stubbed sync endpoints/demo fallbacks:
1. **Google OAuth:** OAuth PKCE URL generator is in place, but lacks CSRF state validation, lacks automatic token refresh, and frontend callback handling needs end-to-end wiring.
2. **Gmail Service:** `gmail_service.py` contains full Gmail API fetch and classification logic, but `POST /api/v1/gmail/sync` returns a static mock JSON summary (`synced_messages_count: 2`) instead of calling `fetch_and_ingest_live_messages`.
3. **Google Calendar Service:** `calendar_service.py` contains event fetch and sync logic, but lacks a dedicated `/calendar/sync` route and token expiration handling.
4. **AI Provider:** `LLMProvider` abstraction supports OpenAI and Gemini with fallback heuristic factories. Requires retry/timeout hardening and explicit status reporting (`CONNECTED` vs `FALLBACK`).
5. **Settings Status Reporting:** Endpoints currently query `demo@pulse.ai`. Integrations status accurately reflects DB `OAuthAccount` state, but requires explicit sub-channel separation for Google Account, Gmail, and Google Calendar.

---

## 2. Component-by-Component Audit Findings

### 2.1 Backend Entry & Config
- **Files:** `backend/app/main.py`, `backend/app/config.py`
- **Current State:** `main.py` properly initializes tables and conditionally seeds demo data when `ENVIRONMENT == "development"`. In `production`, demo seeding is disabled.
- **Findings & Actions:**
  - CORS configuration permits local dev origins and `https://pulse-ai.vercel.app`.
  - `GOOGLE_REDIRECT_URI` is environment configurable.

### 2.2 Google OAuth Implementation
- **Files:** `backend/app/api/v1/auth.py`, `backend/app/models/user.py`
- **Current State:** Supports `/login/google/url`, `/login/google`, `/disconnect`, and `/me`.
- **Gaps & Defects:**
  - **CSRF State Missing:** `get_google_auth_url` does not inject a cryptographically secure `state` parameter into the Google OAuth URL.
  - **Token Refresh Missing:** Access tokens expire after 3600s. No auto-refresh mechanism exists when calling Gmail/Calendar APIs.
  - **Scopes Incomplete:** Missing `openid` and `https://www.googleapis.com/auth/calendar.readonly`.
  - **Callback Architecture:** Google redirects to frontend `GOOGLE_REDIRECT_URI` (`http://localhost:3000/api/auth/callback/google` or production URL). The frontend exchanges the code via `POST /api/v1/auth/login/google`. A dedicated frontend callback route or handler must handle this seamlessly.

### 2.3 Gmail Integration Pipeline
- **Files:** `backend/app/services/gmail_service.py`, `backend/app/api/v1/gmail.py`
- **Current State:** Ingestion pipeline exists (`EmailMessage` deduplication by `message_id`, relevance classification into `ACTION_REQUIRED` / `INFORMATION_ONLY` / `PROMOTIONAL` / `IRRELEVANT`, task extraction).
- **Gaps & Defects:**
  - **Stubbed Endpoint:** `POST /api/v1/gmail/sync` returns hardcoded dict instead of calling `gmail_service.fetch_and_ingest_live_messages`.
  - **Token Expiry:** `fetch_and_ingest_live_messages` fails silently if access token is expired without attempting refresh token exchange.

### 2.4 Google Calendar Integration & Planning Integration
- **Files:** `backend/app/services/calendar_service.py`, `backend/app/api/v1/calendar.py`, `backend/app/services/planner_engine.py`, `backend/app/services/replan_engine.py`
- **Current State:** `CalendarService` converts Google events into internal `CalendarEvent` models. `PlannerEngine` clamps fixed events into work hours and schedules `TaskItem`s around them without overlap.
- **Gaps & Defects:**
  - `POST /api/v1/calendar/sync` endpoint is missing to allow explicit manual/automatic syncing of calendar events.
  - Token refresh needs to be invoked prior to calendar fetch.

### 2.5 AI Provider Abstraction
- **Files:** `backend/app/services/ai_engine/base.py`, `relevance.py`, `extractor.py`, `nli_parser.py`
- **Current State:** Supports `openai` and `gemini` with structured JSON Pydantic validation and heuristic fallbacks.
- **Gaps & Defects:**
  - Needs retry logic with exponential backoff on HTTP 429/500 errors.
  - Timeout and malformed response exception handling should be explicitly caught without leaking raw secret strings.
  - Truthful status reporting: Returns `FALLBACK (HEURISTIC ENGINE)` when `AI_API_KEY` is missing and `CONNECTED (LIVE OPENAI/GEMINI API)` when configured.

### 2.6 Settings & User Integration Status
- **Files:** `backend/app/api/v1/settings.py`, `frontend/src/app/settings/page.tsx`
- **Current State:** Settings page renders status for Google Account, Gmail, Calendar, AI Engine, and Android Companion.
- **Gaps & Defects:**
  - Ensure status strictly requires an active valid token in `OAuthAccount` before marking Google Account, Gmail, or Calendar as `CONNECTED`.

---

## 3. Recommended Implementation Order (Phase 2 Roadmap)

1. **Step 2 — AI Provider Hardening:** Add retries, timeouts, error boundary logging, and strict status reporting.
2. **Step 3 — Google OAuth & CSRF State:** Implement state validation, scope inclusion (`openid`, `calendar.readonly`), auto token refresh helper, and frontend callback page.
3. **Step 4 — Gmail Live Integration & Endpoint Wiring:** Replace stubbed `POST /api/v1/gmail/sync` with live `fetch_and_ingest_live_messages`, add auto-refresh token check.
4. **Step 5 — Google Calendar Integration:** Add `POST /api/v1/calendar/sync`, auto-refresh token check, and verify zero task overlaps over fixed commitments.
5. **Step 6 & 7 — End-to-End Pipeline & Replanning Verification:** Test Gmail -> Extraction -> Task Creation -> Calendar Conflict Check -> Daily Planner -> Versioning -> Replanning.
6. **Step 8 — Natural Language Commands:** Verify NLI parser triggers correct task creation, event addition, or replanning actions.
7. **Step 9 & 10 — Settings UI & Database Safety:** Ensure settings reflect truthful state and Async SQLAlchemy model relations use `selectinload`.
8. **Step 11 & 12 — Security Audit & Automated Test Expansion:** Write unit/integration tests for OAuth state, token refresh, Gmail deduplication, Calendar conflicts, and NLI.
9. **Step 13, 14, 15, 16 — Production Readiness, Demo Isolation & Final Verification Report (`PHASE_2_VERIFICATION.md`).**

---

## 4. Production Blockers & Key Credentials Checklist

| Integration | Requirements / Blockers |
|---|---|
| **Google OAuth** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` configured in Google Cloud Console with authorized redirect URIs. |
| **Gmail API** | Google Cloud OAuth Consent Screen with `gmail.readonly` scope enabled. |
| **Google Calendar API** | Google Cloud OAuth Consent Screen with `calendar.events` and `calendar.readonly` scopes enabled. |
| **AI Provider** | `AI_PROVIDER` (`openai` or `gemini`) and valid `AI_API_KEY`. |
| **Production DB** | `DATABASE_URL` set to PostgreSQL string (`postgresql+asyncpg://...`). |
