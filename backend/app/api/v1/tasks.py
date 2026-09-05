from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.task import TaskItem, TaskTimeRecord, TaskDependency
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompletionRequest
from app.services.replan_engine import replan_engine

from app.utils import ensure_utc, now_utc

router = APIRouter(prefix="/tasks", tags=["Unified Tasks"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("", response_model=List[TaskOut])
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_demo_user_id(db)
    query = select(TaskItem).where(TaskItem.user_id == user_id).options(selectinload(TaskItem.dependencies))
    if status_filter:
        query = query.where(TaskItem.status == status_filter)
    if category:
        query = query.where(TaskItem.category == category)
    
    res = await db.execute(query)
    tasks = res.scalars().all()
    return tasks

@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(req: TaskCreate, db: AsyncSession = Depends(get_db)):
    user_id = await get_demo_user_id(db)
    task = TaskItem(
        user_id=user_id,
        source=req.source,
        source_reference=req.source_reference,
        title=req.title,
        description=req.description,
        category=req.category,
        priority=req.priority,
        status="PENDING",
        deadline=ensure_utc(req.deadline) if req.deadline else None,
        estimated_duration=req.estimated_duration,
        consequence=req.consequence,
        explanation=f"Manually created task ({req.source})"
    )
    db.add(task)
    await db.flush()

    for dep_id in req.dependencies:
        dep = TaskDependency(task_id=task.id, depends_on_task_id=dep_id)
        db.add(dep)

    await db.commit()

    # Trigger automatic replan
    today_str = now_utc().strftime("%Y-%m-%d")
    await replan_engine.execute_replan(db, user_id, today_str, f"User added task: {task.title}")
    
    # Re-fetch fresh instance with dependencies loaded for safe serialization
    stmt = select(TaskItem).where(TaskItem.id == task.id).options(selectinload(TaskItem.dependencies))
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies))
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, req: TaskUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies))
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, val in req.model_dump(exclude_unset=True).items():
        if key == "deadline" and val:
            val = ensure_utc(val)
        setattr(task, key, val)

    await db.commit()
    today_str = now_utc().strftime("%Y-%m-%d")
    await replan_engine.execute_replan(db, task.user_id, today_str, f"Updated task: {task.title}")

    res = await db.execute(select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies)))
    return res.scalar_one()

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies))
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user_id = task.user_id
    await db.delete(task)
    await db.commit()

    today_str = now_utc().strftime("%Y-%m-%d")
    await replan_engine.execute_replan(db, user_id, today_str, f"Deleted task: {task_id}")
    return {"message": "Task deleted successfully", "id": task_id}

@router.post("/{task_id}/complete", response_model=TaskOut)
async def complete_task(
    task_id: str,
    req: TaskCompletionRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies))
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "COMPLETED"
    task.actual_duration = req.actual_duration_minutes
    task.completed_at = now_utc()

    # Time estimation feedback record
    time_rec = TaskTimeRecord(
        task_id=task.id,
        user_id=task.user_id,
        estimated_minutes=task.estimated_duration,
        actual_minutes=req.actual_duration_minutes
    )
    db.add(time_rec)
    await db.commit()

    # Trigger replan to free up slot
    today_str = now_utc().strftime("%Y-%m-%d")
    await replan_engine.execute_replan(db, task.user_id, today_str, f"Completed task: {task.title}")

    # Re-fetch fresh instance for safe response serialization
    res = await db.execute(select(TaskItem).where(TaskItem.id == task_id).options(selectinload(TaskItem.dependencies)))
    return res.scalar_one()

