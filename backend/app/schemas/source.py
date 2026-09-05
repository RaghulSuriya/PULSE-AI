from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class EmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    sender: str
    subject: Optional[str] = None
    snippet: Optional[str] = None
    received_at: datetime
    classification: str
    confidence: float
    reasoning: List[str]
    processed: bool

class NotificationIngestRequest(BaseModel):
    source_app: str  # SMS, Bank, Recharge, Delivery, Calendar
    title: Optional[str] = None
    content: str
    timestamp: Optional[datetime] = None
    device_token: Optional[str] = None

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_app: str
    title: Optional[str] = None
    content: str
    timestamp: datetime
    classification: str
    confidence: float
    reasoning: List[str]
    processed: bool

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    extracted_summary: Optional[str] = None
    processed: bool
    created_at: datetime
