from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.plan import DailyPlan, PlanVersion
from app.schemas.plan import DailyPlanOut, PlanVersionOut, ReplanRequest
from app.services.replan_engine import replan_engine

from app.utils import now_utc

router = APIRouter(prefix="/plans", tags=["AI Daily Schedule & Replanning"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("", response_model=List[DailyPlanOut])
async def list_plans(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(DailyPlan).where(DailyPlan.user_id == user_id).options(selectinload(DailyPlan.items)).order_by(DailyPlan.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=DailyPlanOut, status_code=status.HTTP_201_CREATED)
async def create_or_generate_plan(req: Optional[ReplanRequest] = None, db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    today_str = now_utc().strftime("%Y-%m-%d")
    reason = req.reason if req and req.reason else "Plan Generation Request"
    plan = await replan_engine.execute_replan(db, user_id, today_str, reason)
    stmt = select(DailyPlan).where(DailyPlan.id == plan.id).options(selectinload(DailyPlan.items))
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("/today", response_model=DailyPlanOut)
async def get_today_plan(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    today_str = now_utc().strftime("%Y-%m-%d")
    
    stmt = select(DailyPlan).where(
        DailyPlan.user_id == user_id, 
        DailyPlan.date == today_str
    ).options(selectinload(DailyPlan.items))
    
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    
    if not plan:
        plan = await replan_engine.execute_replan(db, user_id, today_str, "Initial Daily Plan Generation")
        stmt = select(DailyPlan).where(DailyPlan.id == plan.id).options(selectinload(DailyPlan.items))
        res = await db.execute(stmt)
        plan = res.scalar_one()

    return plan

@router.post("/replan", response_model=DailyPlanOut)
async def trigger_replan(req: ReplanRequest, db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    today_str = now_utc().strftime("%Y-%m-%d")
    
    plan = await replan_engine.execute_replan(db, user_id, today_str, req.reason or "Manual User Replan Request")
    
    stmt = select(DailyPlan).where(DailyPlan.id == plan.id).options(selectinload(DailyPlan.items))
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("/versions", response_model=List[PlanVersionOut])
async def get_plan_versions(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    today_str = now_utc().strftime("%Y-%m-%d")
    
    stmt = select(DailyPlan).where(DailyPlan.user_id == user_id, DailyPlan.date == today_str)
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    
    if not plan:
        return []

    v_stmt = select(PlanVersion).where(PlanVersion.plan_id == plan.id).order_by(PlanVersion.version_number.desc())
    v_res = await db.execute(v_stmt)
    return v_res.scalars().all()

