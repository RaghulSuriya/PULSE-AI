from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.ai import AuditLog

router = APIRouter(prefix="/audit", tags=["Execution Verification & Audit Trail"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("/logs")
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()
