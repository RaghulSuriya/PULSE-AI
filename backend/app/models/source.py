import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(255), index=True, nullable=False)
    thread_id = Column(String(255), nullable=True)
    sender = Column(String(255), nullable=False)
    subject = Column(String(512), nullable=True)
    snippet = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    classification = Column(String(50), default="UNCERTAIN") # ACTION_REQUIRED, INFORMATION_ONLY, PROMOTIONAL, IRRELEVANT, UNCERTAIN
    confidence = Column(Float, default=0.0)
    reasoning = Column(JSON, default=list) # List of strings explaining decision
    processed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationItem(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_app = Column(String(100), nullable=False) # SMS, Bank, Recharge, Delivery, Calendar
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    classification = Column(String(50), default="UNCERTAIN")
    confidence = Column(Float, default=0.0)
    reasoning = Column(JSON, default=list)
    processed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentItem(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # pdf, docx, image, txt
    file_path = Column(String(512), nullable=True)
    raw_text = Column(Text, nullable=True)
    
    extracted_summary = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedInformation(Base):
    __tablename__ = "extracted_information"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False) # EMAIL, NOTIFICATION, DOCUMENT, MANUAL_INPUT
    source_id = Column(String(255), nullable=False)
    
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    dates = Column(JSON, default=list)
    deadline = Column(DateTime, nullable=True)
    eligibility = Column(Text, nullable=True)
    amounts = Column(JSON, default=list) # e.g. [{"type": "bill", "amount": "$50"}]
    requirements = Column(JSON, default=list)
    consequences = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
