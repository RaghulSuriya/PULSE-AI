from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.source import EmailMessage
from app.schemas.source import EmailOut

router = APIRouter(prefix="/gmail", tags=["Gmail Integration"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

from app.services.gmail_service import gmail_service
from app.services.replan_engine import replan_engine
from datetime import datetime

@router.get("/messages", response_model=List[EmailOut])
async def list_email_messages(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(EmailMessage).where(EmailMessage.user_id == user_id).order_by(EmailMessage.received_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/sync")
async def trigger_gmail_sync(db: AsyncSession = Depends(get_db)):
    """Triggers incremental Gmail sync pipeline against live Gmail API or stored state."""
    user_id = await get_demo_user_id(db)
    processed_emails = await gmail_service.fetch_and_ingest_live_messages(db, user_id)
    
    actionable_count = sum(1 for e in processed_emails if e.classification == "ACTION_REQUIRED")
    
    if actionable_count > 0:
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await replan_engine.execute_replan(db, user_id, today_str, f"Gmail Sync: {actionable_count} new actionable task(s) ingested")

    return {
        "status": "SUCCESS",
        "synced_messages_count": len(processed_emails),
        "new_actionable_tasks": actionable_count
    }

