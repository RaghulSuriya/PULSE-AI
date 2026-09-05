import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from app.database import Base

class AIDecision(Base):
    __tablename__ = "ai_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision_type = Column(String(50), nullable=False) # CLASSIFICATION, EXTRACTION, SCHEDULING, TIME_ESTIMATE, REPLAN
    
    target_entity_type = Column(String(50), nullable=False) # EMAIL, NOTIFICATION, TASK, PLAN
    target_entity_id = Column(String(255), nullable=False)
    
    decision = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    reasoning = Column(JSON, default=list) # List of bullet points / rules applied
    evidence = Column(JSON, default=dict)   # Raw extracted snippets or factors
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    action_type = Column(String(50), nullable=False) # DETECTED, UNDERSTOOD, PLANNED, APPROVED, EXECUTED, VERIFIED, FAILED
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    description = Column(Text, nullable=False)
    
    verified_status = Column(String(20), default="PENDING") # PENDING, SUCCESS, FAILED
    verification_details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
