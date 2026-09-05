import logging
import httpx
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import OAuthAccount
from app.models.calendar import CalendarEvent

from app.utils import ensure_utc, now_utc, parse_iso_utc

logger = logging.getLogger("pulse.calendar")

class CalendarService:
    """
    Google Calendar API integration & Sync Service.
    Reads fixed events, computes free slots, and writes approved events back safely.
    """

    async def fetch_live_calendar_events(self, db: AsyncSession, user_id: str) -> List[CalendarEvent]:
        """
        Queries live Google Calendar API for primary calendar events using user's OAuth access token.
        """
        from app.api.v1.auth import get_valid_google_token
        access_token = await get_valid_google_token(db, user_id)

        if not access_token:
            logger.info(f"No valid Google OAuth token for user {user_id}. Skipping live Calendar fetch.")
            return []

        headers = {"Authorization": f"Bearer {access_token}"}
        time_min = now_utc().strftime("%Y-%m-%dT00:00:00Z")
        time_max = (now_utc() + timedelta(days=1)).strftime("%Y-%m-%dT23:59:59Z")
        
        cal_url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={time_min}&timeMax={time_max}&singleEvents=true"

        synced_events = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(cal_url, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Google Calendar API fetch failed: {res.status_code} {res.text}")
                    return []

                items = res.json().get("items", [])
                formatted = []
                for item in items:
                    start_str = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
                    end_str = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")
                    if start_str and end_str:
                        formatted.append({
                            "id": item["id"],
                            "title": item.get("summary", "Untitled Event"),
                            "description": item.get("description"),
                            "location": item.get("location"),
                            "start_time": start_str,
                            "end_time": end_str,
                            "category": "WORK"
                        })
                synced_events = await self.sync_user_calendar(db, user_id, formatted)

        except Exception as e:
            logger.error(f"Error fetching live Google Calendar events: {e}")

        return synced_events

    async def sync_user_calendar(self, db: AsyncSession, user_id: str, events_data: List[dict]) -> List[CalendarEvent]:
        synced = []
        for item in events_data:
            google_id = item.get("id")
            stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id, CalendarEvent.google_event_id == google_id)
            existing = (await db.execute(stmt)).scalar_one_or_none()
            
            start_dt = parse_iso_utc(item["start_time"])
            end_dt = parse_iso_utc(item["end_time"])

            if existing:
                existing.title = item["title"]
                existing.start_time = start_dt
                existing.end_time = end_dt
                existing.category = item.get("category", "FIXED")
                synced.append(existing)
            else:
                new_ev = CalendarEvent(
                    user_id=user_id,
                    google_event_id=google_id,
                    title=item["title"],
                    description=item.get("description"),
                    location=item.get("location"),
                    start_time=start_dt,
                    end_time=end_dt,
                    category=item.get("category", "FIXED")
                )
                db.add(new_ev)
                synced.append(new_ev)

        await db.commit()
        return synced

calendar_service = CalendarService()
