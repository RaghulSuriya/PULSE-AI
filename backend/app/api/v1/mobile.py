from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.source import NotificationItem
from app.schemas.source import NotificationIngestRequest, NotificationOut
from app.services.ai_engine.relevance import relevance_classifier
from app.models.task import TaskItem
from app.services.replan_engine import replan_engine

router = APIRouter(prefix="/mobile", tags=["Mobile & Android Companion"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("/notifications", response_model=List[NotificationOut])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(NotificationItem).where(NotificationItem.user_id == user_id).order_by(NotificationItem.timestamp.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/notifications", response_model=NotificationOut)
async def ingest_notification(req: NotificationIngestRequest, db: AsyncSession = Depends(get_db)):
    """
    Ingests notification forwarded securely from Android Companion listener.
    Runs AI Relevance classifier and generates tasks for actionable SMS/alerts.
    """
    user_id = await get_demo_user_id(db)

    # Classify notification text
    classification = await relevance_classifier.classify_communication(req.source_app, req.title or req.source_app, req.content)

    notif_item = NotificationItem(
        user_id=user_id,
        source_app=req.source_app,
        title=req.title,
        content=req.content,
        timestamp=req.timestamp or datetime.utcnow(),
        classification=classification.classification,
        confidence=classification.confidence,
        reasoning=classification.reasoning,
        processed=True
    )
    db.add(notif_item)
    await db.flush()

    if classification.classification == "ACTION_REQUIRED":
        task = TaskItem(
            user_id=user_id,
            source="SMS" if "SMS" in req.source_app or "Bank" in req.source_app else "NOTIFICATION",
            source_reference=notif_item.id,
            title=req.title or f"Action from {req.source_app}",
            description=req.content,
            category="BILLS" if any(k in req.content.lower() for k in ["bill", "due", "pay", "recharge"]) else "GENERAL",
            priority="MUST_DO" if classification.urgency == "HIGH" else "SHOULD_DO",
            status="PENDING",
            estimated_duration=classification.estimated_duration_minutes or 15,
            confidence=classification.confidence,
            consequence=classification.consequence_summary,
            explanation=f"Generated from mobile alert '{req.source_app}' because: " + "; ".join(classification.reasoning)
        )
        db.add(task)
        await db.commit()

        # Trigger automatic replan
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await replan_engine.execute_replan(db, user_id, today_str, f"New mobile alert task: {task.title}")

    else:
        await db.commit()

    await db.refresh(notif_item)
    return notif_item
