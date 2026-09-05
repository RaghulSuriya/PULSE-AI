from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.task import TaskItem, TaskTimeRecord
from app.models.source import EmailMessage, NotificationItem

router = APIRouter(prefix="/insights", tags=["Productivity Insights"])

async def get_demo_user_id(db: AsyncSession) -> str:
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user.id if user else ""

@router.get("")
async def get_productivity_insights(db: AsyncSession = Depends(get_db)):
    """
    Calculates productivity metrics dynamically from database history:
    - Tasks completed vs postponed
    - Estimated vs actual duration accuracy
    - Workload category distribution
    - Source counts
    """
    user_id = await get_demo_user_id(db)

    # Fetch completed tasks
    stmt_completed = select(TaskItem).where(TaskItem.user_id == user_id, TaskItem.status == "COMPLETED")
    res_completed = await db.execute(stmt_completed)
    completed_tasks = res_completed.scalars().all()

    # Fetch all tasks
    stmt_all = select(TaskItem).where(TaskItem.user_id == user_id)
    res_all = await db.execute(stmt_all)
    all_tasks = res_all.scalars().all()

    # Fetch time records
    stmt_time = select(TaskTimeRecord).where(TaskTimeRecord.user_id == user_id)
    res_time = await db.execute(stmt_time)
    time_records = res_time.scalars().all()

    has_sufficient_data = len(completed_tasks) >= 2 or len(all_tasks) >= 3

    # Calculate workload category breakdown dynamically
    category_counts = {}
    for t in all_tasks:
        category_counts[t.category] = category_counts.get(t.category, 0) + (t.estimated_duration or 30)

    total_task_minutes = sum(category_counts.values()) or 1
    workload_breakdown = [
        {
            "category": cat,
            "percentage": round((mins / total_task_minutes) * 100),
            "hours": round(mins / 60.0, 1)
        }
        for cat, mins in category_counts.items()
    ]

    # Calculate time estimation accuracy
    if time_records:
        avg_est = sum(r.estimated_minutes for r in time_records) / len(time_records)
        avg_act = sum(r.actual_minutes for r in time_records) / len(time_records)
        ratio = round(avg_est / max(1.0, avg_act), 2)
        note = f"Based on {len(time_records)} recorded tasks, actual task completion averages {round(avg_act)} minutes vs {round(avg_est)} estimated minutes."
    else:
        avg_est = 30
        avg_act = 35
        ratio = 0.86
        note = "Initial baseline estimates active. Complete more tasks to refine personal focus time model."

    # Source breakdown
    source_counts = {}
    for t in all_tasks:
        source_counts[t.source] = source_counts.get(t.source, 0) + 1

    top_sources = [{"source": src, "count": cnt} for src, cnt in source_counts.items()]

    return {
        "has_sufficient_data": has_sufficient_data,
        "tasks_completed_this_week": len(completed_tasks),
        "tasks_postponed_this_week": len([t for t in all_tasks if t.status == "POSTPONED"]),
        "deadline_success_rate": round(len(completed_tasks) / max(1, len(all_tasks)), 2) if all_tasks else 1.0,
        "time_estimation_accuracy": {
            "ai_estimated_avg_minutes": round(avg_est),
            "user_actual_avg_minutes": round(avg_act),
            "accuracy_ratio": ratio,
            "insight_note": note
        },
        "workload_by_category": workload_breakdown,
        "top_sources": top_sources
    }
