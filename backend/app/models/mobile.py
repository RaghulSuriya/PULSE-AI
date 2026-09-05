import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class MobileDevice(Base):
    __tablename__ = "mobile_devices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_name = Column(String(100), nullable=False)
    device_token = Column(String(255), unique=True, nullable=False)
    android_version = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True)
    enabled_sources = Column(JSON, default=lambda: {
        "sms": True,
        "bank": True,
        "recharge": True,
        "electricity": True,
        "delivery": True,
        "calendar": False
    })
    
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mobile_devices")
