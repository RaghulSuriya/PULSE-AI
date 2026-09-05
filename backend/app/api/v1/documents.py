from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.source import DocumentItem
from app.schemas.source import DocumentOut
from app.services.document_service import document_service
from app.services.replan_engine import replan_engine
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["Document Understanding"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("", response_model=List[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    stmt = select(DocumentItem).where(DocumentItem.user_id == user_id).order_by(DocumentItem.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_demo_user_id(db)
    file_bytes = await file.read()
    
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
    doc_item, tasks_created = await document_service.parse_and_process_document(
        db, user_id, file.filename, file_bytes, file_ext
    )

    if tasks_created > 0:
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await replan_engine.execute_replan(db, user_id, today_str, f"Uploaded document: {file.filename}")

    return doc_item
