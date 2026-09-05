from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    picture: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserPreferencesUpdate(BaseModel):
    occupation: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    sleep_start_time: Optional[str] = None
    wake_time: Optional[str] = None
    preferred_focus_duration: Optional[int] = None
    buffer_duration_between_tasks: Optional[int] = None
    notification_channels: Optional[dict] = None
    news_categories: Optional[List[str]] = None
    demo_mode: Optional[bool] = None

class UserPreferencesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    occupation: str
    work_start_time: str
    work_end_time: str
    sleep_start_time: str
    wake_time: str
    preferred_focus_duration: int
    buffer_duration_between_tasks: int
    notification_channels: dict
    news_categories: List[str]
    demo_mode: bool

class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    preferences: Optional[UserPreferencesOut] = None
