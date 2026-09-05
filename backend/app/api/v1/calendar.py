from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.calendar import CalendarEvent

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

from app.services.calendar_service import calendar_service
from app.services.replan_engine import replan_engine
from datetime import datetime

@router.get("/events")
async def list_calendar_events(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.start_time.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/sync")
async def trigger_calendar_sync(db: AsyncSession = Depends(get_db)):
    """Fetches live primary calendar events from Google Calendar API and updates daily schedule."""
    user_id = await get_demo_user_id(db)
    synced_events = await calendar_service.fetch_live_calendar_events(db, user_id)
    
    if len(synced_events) > 0:
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await replan_engine.execute_replan(db, user_id, today_str, f"Google Calendar Sync: {len(synced_events)} events updated")

    return {
        "status": "SUCCESS",
        "synced_events_count": len(synced_events)
    }

