import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

@pytest.mark.asyncio
async def test_integrations_status_reporting():
    """Verifies that /api/v1/settings/integrations reports truthful, environment-aware state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/settings/integrations")
        assert resp.status_code == 200
        data = resp.json()
        assert "google_account" in data
        assert "gmail" in data
        assert "google_calendar" in data
        assert "ai_provider" in data
        assert "mobile_companion" in data
        assert data["ai_provider"]["status"].startswith("CONNECTED") or data["ai_provider"]["status"].startswith("FALLBACK")

@pytest.mark.asyncio
async def test_google_auth_url_generation():
    """Verifies that Google OAuth URL includes state parameter and required scopes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/auth/login/google/url")
        assert resp.status_code == 200
        data = resp.json()
        assert "auth_url" in data
        assert "state=" in data["auth_url"]
        assert "gmail.readonly" in data["auth_url"]
        assert "calendar.events" in data["auth_url"]

@pytest.mark.asyncio
async def test_natural_language_input_processing():
    """Verifies that NLI parser handles task creation, calendar event, and replanning triggers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test task creation
        res1 = await ac.post("/api/v1/ai/nli", json={"text": "Study AWS tomorrow for 2 hours"})
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["intent"] in ["CREATE_TASK", "ADD_CALENDAR_EVENT"]

        # Test replanning request
        res2 = await ac.post("/api/v1/ai/nli", json={"text": "I couldn't finish my assignment today, please replan my day"})
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["intent"] == "REPLAN_DAY"

@pytest.mark.asyncio
async def test_gmail_and_calendar_sync_endpoints():
    """Verifies that Gmail and Calendar sync endpoints run without server errors."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        gmail_res = await ac.post("/api/v1/gmail/sync")
        assert gmail_res.status_code == 200
        gmail_data = gmail_res.json()
        assert gmail_data["status"] == "SUCCESS"

        cal_res = await ac.post("/api/v1/calendar/sync")
        assert cal_res.status_code == 200
        cal_data = cal_res.json()
        assert cal_data["status"] == "SUCCESS"

