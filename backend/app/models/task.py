import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class TaskItem(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    source = Column(String(50), nullable=False) # EMAIL, SMS, NOTIFICATION, DOCUMENT, CALENDAR, MANUAL_INPUT, USER_CREATED, RECURRING_TASK
    source_reference = Column(String(255), nullable=True) # ID of email/notification/doc
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="GENERAL") # COLLEGE, WORK, BILLS, PERSONAL, OPPORTUNITY, GENERAL
    priority = Column(String(20), default="SHOULD_DO") # MUST_DO, SHOULD_DO, CAN_MOVE, OPTIONAL
    status = Column(String(20), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, SKIPPED, POSTPONED
    
    deadline = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, default=30) # minutes
    actual_duration = Column(Integer, nullable=True) # minutes
    
    confidence = Column(Float, default=1.0)
    consequence = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True) # AI rationale for creation & prioritization

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")
    dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.task_id", back_populates="task", cascade="all, delete-orphan")
    time_records = relationship("TaskTimeRecord", back_populates="task", cascade="all, delete-orphan")

    @property
    def dependency_ids(self) -> list:
        if "dependencies" in self.__dict__ and self.dependencies is not None:
            return [d.depends_on_task_id for d in self.dependencies]
        return []

class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    depends_on_task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("TaskItem", foreign_keys=[task_id], back_populates="dependencies")
    depends_on = relationship("TaskItem", foreign_keys=[depends_on_task_id])

class TaskTimeRecord(Base):
    __tablename__ = "task_time_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    estimated_minutes = Column(Integer, nullable=False)
    actual_minutes = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("TaskItem", back_populates="time_records")
