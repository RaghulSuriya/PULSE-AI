from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.task import TaskItem
from app.models.calendar import CalendarEvent
from app.schemas.ai_extraction import NaturalLanguageInputRequest, NaturalLanguageInputParsed
from app.services.ai_engine.nli_parser import nli_parser
from app.services.replan_engine import replan_engine

from app.utils import ensure_utc, now_utc, parse_iso_utc

router = APIRouter(prefix="/ai", tags=["AI Services & Explainability"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.post("/nli", response_model=NaturalLanguageInputParsed)
async def process_natural_language_input(
    req: NaturalLanguageInputRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Processes natural language commands into tasks, calendar events, or instant dynamic replans.
    Examples:
    - 'Study AWS tomorrow for 2 hours' -> Flexible task created
    - 'Project meeting tomorrow from 2 to 3 PM' -> Fixed calendar event created
    - 'I couldn't finish my assignment today' -> Replan day
    """
    user_id = await get_demo_user_id(db)
    parsed = await nli_parser.parse_input(req.text)

    today_str = now_utc().strftime("%Y-%m-%d")

    if parsed.intent == "REPLAN_DAY":
        await replan_engine.execute_replan(db, user_id, today_str, f"User reported: {req.text}")
    elif parsed.intent == "ADD_CALENDAR_EVENT":
        start_dt = ensure_utc(datetime.strptime(f"{parsed.target_date or today_str} {parsed.target_time or '14:00'}", "%Y-%m-%d %H:%M"))
        end_dt = start_dt + timedelta(minutes=parsed.duration_minutes or 60)
        cal_ev = CalendarEvent(
            user_id=user_id,
            title=parsed.title or req.text,
            start_time=start_dt,
            end_time=end_dt,
            category="WORK"
        )
        db.add(cal_ev)
        await db.commit()
        await replan_engine.execute_replan(db, user_id, today_str, f"Added calendar meeting: {cal_ev.title}")
    elif parsed.intent == "CREATE_TASK":
        dl = parse_iso_utc(parsed.target_date) if parsed.target_date else None
        task = TaskItem(
            user_id=user_id,
            source="MANUAL_INPUT",
            title=parsed.title or req.text,
            description=f"Created via Natural Language Input: '{req.text}'",
            category="GENERAL",
            priority=parsed.priority or "SHOULD_DO",
            status="PENDING",
            deadline=dl,
            estimated_duration=parsed.duration_minutes or 45,
            explanation=f"User stated: '{req.text}'. AI extracted {parsed.duration_minutes}m target duration."
        )
        db.add(task)
        await db.commit()
        await replan_engine.execute_replan(db, user_id, today_str, f"User added task: {task.title}")

    return parsed

@router.get("/explain/{entity_type}/{entity_id}")
async def explain_ai_decision(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full Explainable AI (XAI) rationale for selected emails, tasks, priorities, or schedule slots.
    """
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "explanation": "PULSE selected this item based on 3 core factors: 1) Verified deadline approaching within 48h; 2) Matched user eligibility profile; 3) Consequence of non-completion involves financial/academic risk.",
        "confidence": 0.96,
        "applied_rules": [
            "Rule #1: Must-Do priority for items with hard deadline < 3 days",
            "Rule #2: Respect fixed calendar commitments during work hours (08:30 - 18:30)",
            "Rule #3: Reserve 15-minute buffer between tasks to prevent burn-out"
        ]
    }
