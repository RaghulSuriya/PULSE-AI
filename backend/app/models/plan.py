import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class DailyPlan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String(10), nullable=False) # YYYY-MM-DD format
    
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    available_minutes = Column(Integer, default=400)
    fixed_minutes = Column(Integer, default=120)
    planned_workload_minutes = Column(Integer, default=280)
    overload_minutes = Column(Integer, default=0)
    is_overloaded = Column(Boolean, default=False)
    
    summary_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")
    versions = relationship("PlanVersion", back_populates="plan", cascade="all, delete-orphan")

class PlanVersion(Base):
    __tablename__ = "plan_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    trigger_reason = Column(Text, nullable=False) # e.g. "User added task: AWS Study", "Task missed: Assignment"
    
    changes_summary = Column(JSON, default=list) # List of string descriptions of what changed
    snapshot_items = Column(JSON, default=list) # Serialized list of plan items at this version
    
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("DailyPlan", back_populates="versions")

class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    calendar_event_id = Column(String(36), ForeignKey("calendar_events.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    start_time = Column(String(5), nullable=False) # HH:MM
    end_time = Column(String(5), nullable=False)   # HH:MM
    duration_minutes = Column(Integer, nullable=False)
    
    item_type = Column(String(50), default="TASK") # TASK, FIXED_EVENT, BUFFER, ROUTINE
    status = Column(String(20), default="SCHEDULED") # SCHEDULED, COMPLETED, SKIPPED, MOVED
    
    reason = Column(Text, nullable=True) # Explainable AI reason why scheduled at this slot
    
    plan = relationship("DailyPlan", back_populates="items")
