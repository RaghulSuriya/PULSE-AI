from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.plan import DailyPlan, PlanVersion, PlanItem
from app.models.task import TaskItem
from app.models.calendar import CalendarEvent
from app.models.user import UserPreferences
from app.services.planner_engine import planner_engine

class ReplanEngine:
    """
    Dynamic Replanning Service.
    Recalculates optimized schedule when events change, tasks are delayed, or new emails arrive.
    Maintains Plan Versions and computes explicit diff summaries ("What changed?").
    """

    async def execute_replan(
        self,
        db: AsyncSession,
        user_id: str,
        date_str: str,
        trigger_reason: str
    ) -> DailyPlan:
        from sqlalchemy.orm import selectinload

        # Fetch user preferences
        pref_result = await db.execute(select(UserPreferences).where(UserPreferences.user_id == user_id))
        user_prefs = pref_result.scalar_one_or_none()

        # Fetch active tasks and calendar events with dependencies loaded
        task_result = await db.execute(
            select(TaskItem)
            .where(TaskItem.user_id == user_id, TaskItem.status != "COMPLETED")
            .options(selectinload(TaskItem.dependencies))
        )
        tasks = task_result.scalars().all()

        cal_result = await db.execute(select(CalendarEvent).where(CalendarEvent.user_id == user_id))
        calendar_events = cal_result.scalars().all()

        # Fetch or create plan entity with items preloaded
        plan_result = await db.execute(
            select(DailyPlan)
            .where(DailyPlan.user_id == user_id, DailyPlan.date == date_str)
            .options(selectinload(DailyPlan.items))
        )
        plan = plan_result.scalar_one_or_none()

        if not plan:
            plan = DailyPlan(
                user_id=user_id,
                date=date_str,
                version=1,
                is_active=True
            )
            db.add(plan)
            await db.flush()
        else:
            plan.version += 1

        # Calculate new plan configuration
        plan_data = planner_engine.build_daily_plan(date_str, user_prefs, calendar_events, tasks)

        plan.available_minutes = plan_data["available_minutes"]
        plan.fixed_minutes = plan_data["fixed_minutes"]
        plan.planned_workload_minutes = plan_data["planned_workload_minutes"]
        plan.overload_minutes = plan_data["overload_minutes"]
        plan.is_overloaded = plan_data["is_overloaded"]
        plan.summary_explanation = plan_data["summary_explanation"]

        # Clear existing plan items
        await db.execute(select(PlanItem).where(PlanItem.plan_id == plan.id))
        # Delete old items
        for old_item in plan.items:
            await db.delete(old_item)

        # Insert new plan items
        new_items = []
        for item in plan_data["items"]:
            pi = PlanItem(
                plan_id=plan.id,
                task_id=item.get("task_id"),
                title=item["title"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                duration_minutes=item["duration_minutes"],
                item_type=item["item_type"],
                status=item["status"],
                reason=item.get("reason")
            )
            db.add(pi)
            new_items.append(pi)

        # Create Version Record Snapshot
        changes_diff = [
            f"Plan updated to Version {plan.version}",
            f"Trigger: {trigger_reason}",
            f"Preserved fixed calendar commitments ({plan.fixed_minutes} mins)"
        ]
        if plan.is_overloaded:
            changes_diff.append(f"Adjusted schedule due to {plan.overload_minutes}m capacity overload")

        plan_version = PlanVersion(
            plan_id=plan.id,
            version_number=plan.version,
            trigger_reason=trigger_reason,
            changes_summary=changes_diff,
            snapshot_items=[{
                "title": i["title"],
                "start_time": i["start_time"],
                "end_time": i["end_time"],
                "item_type": i["item_type"]
            } for i in plan_data["items"]]
        )
        db.add(plan_version)

        await db.commit()
        await db.refresh(plan)
        return plan

replan_engine = ReplanEngine()
