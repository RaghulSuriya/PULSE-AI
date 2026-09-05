from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PlanItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: Optional[str] = None
    calendar_event_id: Optional[str] = None
    title: str
    start_time: str
    end_time: str
    duration_minutes: int
    item_type: str
    status: str
    reason: Optional[str] = None

class PlanVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version_number: int
    trigger_reason: str
    changes_summary: List[str]
    snapshot_items: List[dict]
    created_at: datetime

class DailyPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    date: str
    version: int
    is_active: bool
    available_minutes: int
    fixed_minutes: int
    planned_workload_minutes: int
    overload_minutes: int
    is_overloaded: bool
    summary_explanation: Optional[str] = None
    items: List[PlanItemOut] = []
    created_at: datetime

class ReplanRequest(BaseModel):
    reason: Optional[str] = "Manual user replan request"
