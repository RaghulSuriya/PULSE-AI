from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User, UserPreferences
from app.schemas.auth import UserOut, UserPreferencesUpdate, UserPreferencesOut

router = APIRouter(prefix="/users", tags=["Users & Preferences"])

@router.get("/me/preferences", response_model=UserPreferencesOut)
async def get_preferences(db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == "demo@pulse.ai").options(selectinload(User.preferences))
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not user.preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return user.preferences

@router.patch("/me/preferences", response_model=UserPreferencesOut)
async def update_preferences(req: UserPreferencesUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == "demo@pulse.ai").options(selectinload(User.preferences))
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not user.preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")

    prefs = user.preferences
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(prefs, key, val)

    await db.commit()
    await db.refresh(prefs)
    return prefs
