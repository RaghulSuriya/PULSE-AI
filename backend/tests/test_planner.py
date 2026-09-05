from datetime import datetime
from app.models.user import UserPreferences
from app.models.task import TaskItem
from app.models.calendar import CalendarEvent
from app.services.planner_engine import planner_engine
from app.utils import now_utc

def test_attention_budget_and_slot_allocation():
    user_prefs = UserPreferences(
        work_start_time="09:00",
        work_end_time="17:00",
        buffer_duration_between_tasks=15
    )

    # 1 Fixed Event: 12:00 to 13:00
    today_str = now_utc().strftime("%Y-%m-%d")
    fixed_event = CalendarEvent(
        title="Team Sync",
        start_time=datetime.strptime(f"{today_str} 12:00", "%Y-%m-%d %H:%M"),
        end_time=datetime.strptime(f"{today_str} 13:00", "%Y-%m-%d %H:%M")
    )

    # 2 Tasks
    task1 = TaskItem(
        id="t1",
        title="Submit Assignment",
        priority="MUST_DO",
        estimated_duration=60,
        status="PENDING"
    )
    task2 = TaskItem(
        id="t2",
        title="Review PRs",
        priority="SHOULD_DO",
        estimated_duration=45,
        status="PENDING"
    )

    plan = planner_engine.build_daily_plan(today_str, user_prefs, [fixed_event], [task1, task2])

    assert plan["available_minutes"] == 480  # 8 hours = 480 mins
    assert plan["fixed_minutes"] == 60       # 1 hour meeting
    assert plan["planned_workload_minutes"] == 105 # 60 + 45
    assert not plan["is_overloaded"]

    # Verify task1 scheduled before meeting
    items = plan["items"]
    t1_item = next(i for i in items if i.get("task_id") == "t1")
    assert t1_item["start_time"] == "09:00"
    assert t1_item["end_time"] == "10:00"
