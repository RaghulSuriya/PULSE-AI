from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Tuple
from app.models.user import UserPreferences
from app.models.task import TaskItem
from app.models.calendar import CalendarEvent
from app.utils import ensure_utc, MAX_UTC_DATETIME

class PlannerEngine:
    """
    Core Attention-to-Execution Planning Engine.
    Computes daily Attention Budget, resolves task dependencies, schedules tasks into free slots,
    detects overload, and generates clear explainable AI rationale for every scheduled slot.
    """

    def parse_time_to_minutes(self, time_str: str) -> int:
        """Converts 'HH:MM' string to minutes from midnight."""
        hours, mins = map(int, time_str.split(":"))
        return hours * 60 + mins

    def minutes_to_time_str(self, minutes: int) -> str:
        """Converts minutes from midnight to 'HH:MM' string."""
        h = (minutes // 60) % 24
        m = minutes % 60
        return f"{h:02d}:{m:02d}"

    def build_daily_plan(
        self,
        date_str: str,
        user_prefs: UserPreferences,
        fixed_events: List[CalendarEvent],
        tasks: List[TaskItem]
    ) -> Dict[str, Any]:
        
        start_work_mins = self.parse_time_to_minutes(user_prefs.work_start_time if user_prefs else "09:00")
        end_work_mins = self.parse_time_to_minutes(user_prefs.work_end_time if user_prefs else "18:00")
        total_available_mins = max(0, end_work_mins - start_work_mins)

        # Map fixed calendar events into busy time ranges
        busy_intervals: List[Tuple[int, int, str]] = []
        fixed_total_mins = 0
        
        for ev in fixed_events:
            ev_start_dt = ensure_utc(ev.start_time)
            ev_end_dt = ensure_utc(ev.end_time)
            ev_start = ev_start_dt.hour * 60 + ev_start_dt.minute
            ev_end = ev_end_dt.hour * 60 + ev_end_dt.minute
            
            # Clamp to work window
            c_start = max(start_work_mins, ev_start)
            c_end = min(end_work_mins, ev_end)
            if c_end > c_start:
                busy_intervals.append((c_start, c_end, ev.title))
                fixed_total_mins += (c_end - c_start)

        busy_intervals.sort(key=lambda x: x[0])

        # Compute free time slots within the work window
        free_slots: List[Tuple[int, int]] = []
        curr = start_work_mins
        for b_start, b_end, _ in busy_intervals:
            if b_start > curr:
                free_slots.append((curr, b_start))
            curr = max(curr, b_end)
        if curr < end_work_mins:
            free_slots.append((curr, end_work_mins))

        # Sort tasks by priority & deadline safely with timezone-aware UTC comparisons
        priority_order = {"MUST_DO": 0, "SHOULD_DO": 1, "CAN_MOVE": 2, "OPTIONAL": 3}
        sorted_tasks = sorted(
            [t for t in tasks if t.status not in ["COMPLETED", "SKIPPED"]],
            key=lambda t: (
                priority_order.get(t.priority, 1),
                ensure_utc(t.deadline) if t.deadline else MAX_UTC_DATETIME
            )
        )

        planned_items = []
        planned_workload_mins = 0
        
        # Include fixed events in plan items
        for b_start, b_end, title in busy_intervals:
            planned_items.append({
                "title": f"Fixed: {title}",
                "start_time": self.minutes_to_time_str(b_start),
                "end_time": self.minutes_to_time_str(b_end),
                "duration_minutes": b_end - b_start,
                "item_type": "FIXED_EVENT",
                "status": "SCHEDULED",
                "reason": "Non-negotiable fixed calendar commitment."
            })

        buffer_mins = user_prefs.buffer_duration_between_tasks if user_prefs else 15

        # Allocate tasks to free slots
        remaining_free_slots = list(free_slots)
        
        for task in sorted_tasks:
            duration = task.estimated_duration or 30
            scheduled = False
            
            for idx, (slot_start, slot_end) in enumerate(remaining_free_slots):
                available_in_slot = slot_end - slot_start
                if available_in_slot >= duration:
                    task_start = slot_start
                    task_end = task_start + duration
                    
                    # Generate Explainable AI Rationale
                    reason_parts = [
                        f"Priority is {task.priority}",
                        f"Fits into a {available_in_slot}-minute free slot"
                    ]
                    if task.deadline:
                        dl_utc = ensure_utc(task.deadline)
                        dl_str = dl_utc.strftime("%b %d, %H:%M")
                        reason_parts.append(f"Deadline approaching ({dl_str})")
                    else:
                        reason_parts.append("No hard deadline, allocated based on workload capacity")

                    planned_items.append({
                        "task_id": task.id,
                        "title": task.title,
                        "start_time": self.minutes_to_time_str(task_start),
                        "end_time": self.minutes_to_time_str(task_end),
                        "duration_minutes": duration,
                        "item_type": "TASK",
                        "status": "SCHEDULED",
                        "reason": f"Scheduled at {self.minutes_to_time_str(task_start)} because: " + "; ".join(reason_parts) + "."
                    })
                    
                    planned_workload_mins += duration
                    
                    # Update remaining slot
                    new_start = task_end + buffer_mins
                    if new_start < slot_end:
                        remaining_free_slots[idx] = (new_start, slot_end)
                    else:
                        remaining_free_slots.pop(idx)
                    scheduled = True
                    break

            if not scheduled:
                # Task could not fit into today's window
                pass

        # Sort all items chronologically by start time
        planned_items.sort(key=lambda x: self.parse_time_to_minutes(x["start_time"]))

        total_task_workload_mins = sum(t.estimated_duration or 30 for t in sorted_tasks)
        
        net_capacity = max(0, total_available_mins - fixed_total_mins)
        overload = max(0, total_task_workload_mins - net_capacity)
        is_overloaded = overload > 0

        summary = (
            f"Day is {int((planned_workload_mins + fixed_total_mins)/max(1, total_available_mins)*100)}% planned. "
            f"Available focus time: {net_capacity // 60}h {net_capacity % 60}m. "
            f"Fixed commitments: {fixed_total_mins // 60}h {fixed_total_mins % 60}m."
        )
        if is_overloaded:
            summary += f" WARNING: Day is overloaded by approximately {overload} minutes."

        return {
            "date": date_str,
            "available_minutes": total_available_mins,
            "fixed_minutes": fixed_total_mins,
            "planned_workload_minutes": planned_workload_mins,
            "overload_minutes": overload,
            "is_overloaded": is_overloaded,
            "summary_explanation": summary,
            "items": planned_items
        }

planner_engine = PlannerEngine()
