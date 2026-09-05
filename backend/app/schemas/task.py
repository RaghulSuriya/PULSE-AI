from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "GENERAL"
    priority: str = "SHOULD_DO"
    deadline: Optional[datetime] = None
    estimated_duration: int = 30
    source: str = "USER_CREATED"
    source_reference: Optional[str] = None
    consequence: Optional[str] = None
    dependencies: List[str] = [] # Task IDs

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    consequence: Optional[str] = None

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    source: str
    source_reference: Optional[str] = None
    title: str
    description: Optional[str] = None
    category: str
    priority: str
    status: str
    deadline: Optional[datetime] = None
    estimated_duration: int
    actual_duration: Optional[int] = None
    confidence: float
    consequence: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    dependency_ids: List[str] = []

class TaskCompletionRequest(BaseModel):
    actual_duration_minutes: int
