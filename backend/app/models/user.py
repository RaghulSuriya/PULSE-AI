import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    picture = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("TaskItem", back_populates="user", cascade="all, delete-orphan")
    plans = relationship("DailyPlan", back_populates="user", cascade="all, delete-orphan")
    mobile_devices = relationship("MobileDevice", back_populates="user", cascade="all, delete-orphan")

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False, default="google") # google
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="oauth_accounts")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    occupation = Column(String(100), default="Professional / Student")
    work_start_time = Column(String(5), default="09:00")  # HH:MM format
    work_end_time = Column(String(5), default="18:00")    # HH:MM format
    sleep_start_time = Column(String(5), default="23:00")
    wake_time = Column(String(5), default="07:00")
    preferred_focus_duration = Column(Integer, default=45) # minutes
    buffer_duration_between_tasks = Column(Integer, default=15) # minutes
    notification_channels = Column(JSON, default=lambda: {"email": True, "mobile": True, "calendar": True})
    news_categories = Column(JSON, default=lambda: ["AI & Technology", "Cloud Computing", "Business", "World", "Science"])
    demo_mode = Column(Boolean, default=True) # Enables seed data demonstration if true
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")
