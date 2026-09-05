import pytest
from datetime import datetime
from app.models.user import UserPreferences
from app.models.task import TaskItem
from app.services.planner_engine import planner_engine
from app.utils import now_utc

def test_overload_detection():
    user_prefs = UserPreferences(
        work_start_time="09:00",
        work_end_time="11:00", # Only 2 hours = 120 mins available
        buffer_duration_between_tasks=10
    )

    today_str = now_utc().strftime("%Y-%m-%d")
    
    # 3 Tasks totaling 180 minutes (exceeding 120 mins)
    task1 = TaskItem(id="t1", title="Task 1", priority="MUST_DO", estimated_duration=60, status="PENDING")
    task2 = TaskItem(id="t2", title="Task 2", priority="MUST_DO", estimated_duration=60, status="PENDING")
    task3 = TaskItem(id="t3", title="Task 3", priority="SHOULD_DO", estimated_duration=60, status="PENDING")

    plan = planner_engine.build_daily_plan(today_str, user_prefs, [], [task1, task2, task3])

    assert plan["is_overloaded"]
    assert "WARNING: Day is overloaded" in plan["summary_explanation"]
