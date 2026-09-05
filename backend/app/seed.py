import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserPreferences
from app.models.source import EmailMessage, NotificationItem, DocumentItem
from app.models.task import TaskItem, TaskDependency, TaskTimeRecord
from app.models.calendar import CalendarEvent
from app.models.plan import DailyPlan, PlanItem, PlanVersion
from app.models.ai import AIDecision, AuditLog
from app.services.planner_engine import planner_engine

from app.utils import ensure_utc, now_utc

logger = logging.getLogger("pulse.seed")

async def seed_demo_data(db: AsyncSession) -> User:
    # Check if demo user exists
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()

    if user:
        logger.info("Demo user already exists.")
        return user

    logger.info("Seeding realistic PULSE AI demo environment...")

    user = User(
        email="demo@pulse.ai",
        full_name="Alex Chen",
        picture="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
    )
    db.add(user)
    await db.flush()

    user_prefs = UserPreferences(
        user_id=user.id,
        occupation="Senior CS Undergrad / Tech Fellow",
        work_start_time="08:30",
        work_end_time="18:30",
        sleep_start_time="23:00",
        wake_time="07:00",
        preferred_focus_duration=45,
        buffer_duration_between_tasks=15,
        demo_mode=True
    )
    db.add(user_prefs)

    # 1. Fixed Calendar Events
    today_str = now_utc().strftime("%Y-%m-%d")
    now_dt = now_utc()

    event1 = CalendarEvent(
        user_id=user.id,
        google_event_id="cal_evt_1",
        title="College CS401 Lab Lecture",
        description="Mandatory attendance for Operating Systems lab",
        start_time=ensure_utc(datetime.strptime(f"{today_str} 09:00", "%Y-%m-%d %H:%M")),
        end_time=ensure_utc(datetime.strptime(f"{today_str} 10:30", "%Y-%m-%d %H:%M")),
        category="COLLEGE"
    )
    event2 = CalendarEvent(
        user_id=user.id,
        google_event_id="cal_evt_2",
        title="Project Sync with Mentor",
        description="Discuss distributed architecture proposal",
        start_time=ensure_utc(datetime.strptime(f"{today_str} 14:00", "%Y-%m-%d %H:%M")),
        end_time=ensure_utc(datetime.strptime(f"{today_str} 15:00", "%Y-%m-%d %H:%M")),
        category="WORK"
    )
    db.add_all([event1, event2])

    # 2. Email Messages
    email1 = EmailMessage(
        user_id=user.id,
        message_id="msg_gmail_101",
        sender="placement-cell@university.edu",
        subject="URGENT: Google Cloud Internship Application 2026",
        snippet="Submit your resume, semester 6 marksheets and bonafide certificate before Sept 20.",
        body_text="Dear Student, Google Cloud Summer Internship applications are now open. Eligible candidates must have minimum 7.5 CGPA. Mandatory documents: Resume PDF, S6 Marksheet, and HOD Bonafide.",
        received_at=now_dt - timedelta(hours=3),
        classification="ACTION_REQUIRED",
        confidence=0.96,
        reasoning=[
            "Contains application deadline (Sept 20)",
            "Mandatory document submission required",
            "High impact career opportunity matched to profile"
        ],
        processed=True
    )
    email2 = EmailMessage(
        user_id=user.id,
        message_id="msg_gmail_102",
        sender="newsletter@techdigest.io",
        subject="Top 10 AI Tools This Week - 50% Off Annual Pass",
        snippet="Check out our curated list of productivity tools with exclusive discounts.",
        body_text="Hi tech enthusiast, upgrade your stack today with half price discounts.",
        received_at=now_dt - timedelta(hours=5),
        classification="PROMOTIONAL",
        confidence=0.94,
        reasoning=["Marketing promotion without mandatory task required"],
        processed=True
    )
    db.add_all([email1, email2])

    # 3. Mobile Notifications
    notif1 = NotificationItem(
        user_id=user.id,
        source_app="Electricity Board SMS",
        title="Electricity Bill Due Warning",
        content="Consumer #984210: Bill amount $64.50 due on Sept 10. Avoid late surcharge of $10.",
        timestamp=now_dt - timedelta(minutes=45),
        classification="ACTION_REQUIRED",
        confidence=0.98,
        reasoning=["Financial payment deadline detected", "Penalty surcharge risk if unpaid"],
        processed=True
    )
    notif2 = NotificationItem(
        user_id=user.id,
        source_app="Mobile Operator",
        title="Recharge Reminder",
        content="Your monthly 5G data plan expires in 2 days. Recharge now to avoid disconnection.",
        timestamp=now_dt - timedelta(hours=1),
        classification="ACTION_REQUIRED",
        confidence=0.91,
        reasoning=["Service continuity deadline"],
        processed=True
    )
    db.add_all([notif1, notif2])

    # 4. Actionable Tasks
    task1 = TaskItem(
        user_id=user.id,
        source="EMAIL",
        source_reference=email1.id,
        title="Obtain HOD Bonafide Certificate",
        description="Visit HOD office to collect signed bonafide for internship application",
        category="COLLEGE",
        priority="MUST_DO",
        status="PENDING",
        deadline=now_dt + timedelta(days=2),
        estimated_duration=45,
        confidence=0.96,
        consequence="Cannot submit Google Cloud internship application without official certificate",
        explanation="Scheduled early morning to accommodate department working hours."
    )
    task2 = TaskItem(
        user_id=user.id,
        source="EMAIL",
        source_reference=email1.id,
        title="Complete Google Cloud Internship Application",
        description="Upload resume, marksheets, and bonafide to placement portal",
        category="COLLEGE",
        priority="MUST_DO",
        status="PENDING",
        deadline=now_dt + timedelta(days=2),
        estimated_duration=30,
        confidence=0.96,
        consequence="Opportunity to interview with Google Cloud will be forfeited if missed.",
        explanation="Requires Bonafide Certificate as a prerequisite dependency."
    )
    task3 = TaskItem(
        user_id=user.id,
        source="SMS",
        source_reference=notif1.id,
        title="Pay Electricity Bill ($64.50)",
        description="Pay via utility banking portal before Sept 10",
        category="BILLS",
        priority="SHOULD_DO",
        status="PENDING",
        deadline=now_dt + timedelta(days=3),
        estimated_duration=10,
        confidence=0.98,
        consequence="Potential $10 late surcharge fee and service disruption.",
        explanation="Short 10-minute task scheduled in afternoon free slot."
    )
    task4 = TaskItem(
        user_id=user.id,
        source="MANUAL_INPUT",
        title="Study AWS Certified Solutions Architect for 1 Hour",
        description="Review VPC networking & IAM policies module",
        category="WORK",
        priority="SHOULD_DO",
        status="PENDING",
        estimated_duration=60,
        confidence=1.0,
        consequence="Delays personal skill certification timeline.",
        explanation="Scheduled during late afternoon focus block."
    )
    db.add_all([task1, task2, task3, task4])
    await db.flush()

    # Task Dependency: Task 2 depends on Task 1
    dep = TaskDependency(task_id=task2.id, depends_on_task_id=task1.id)
    db.add(dep)

    # 5. Build Initial Daily Plan
    plan_data = planner_engine.build_daily_plan(today_str, user_prefs, [event1, event2], [task1, task2, task3, task4])

    plan = DailyPlan(
        user_id=user.id,
        date=today_str,
        version=1,
        is_active=True,
        available_minutes=plan_data["available_minutes"],
        fixed_minutes=plan_data["fixed_minutes"],
        planned_workload_minutes=plan_data["planned_workload_minutes"],
        overload_minutes=plan_data["overload_minutes"],
        is_overloaded=plan_data["is_overloaded"],
        summary_explanation=plan_data["summary_explanation"]
    )
    db.add(plan)
    await db.flush()

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

    # Version record
    pv = PlanVersion(
        plan_id=plan.id,
        version_number=1,
        trigger_reason="Initial Morning AI Attention Synthesis",
        changes_summary=[
            "Synthesized 2 Gmail messages and 2 mobile notifications",
            "Scheduled 4 high-value actionable tasks around 2 fixed calendar events",
            "Attention budget allocated: 4h 35m planned work out of 8h 30m free capacity"
        ],
        snapshot_items=[{"title": i["title"], "start_time": i["start_time"]} for i in plan_data["items"]]
    )
    db.add(pv)

    # 6. Audit & Decisions trace
    audit = AuditLog(
        user_id=user.id,
        action_type="PLANNED",
        risk_level="LOW",
        description="Generated optimized daily schedule for 2026-09-05",
        verified_status="SUCCESS",
        verification_details="Non-conflicting schedule validated against Google Calendar API."
    )
    db.add(audit)

    await db.commit()
    logger.info("Demo data successfully seeded!")
    return user
