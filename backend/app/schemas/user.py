from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, time

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    reminder_time: Optional[time] = None

class User(UserBase):
    id: int
    name: Optional[str] = None
    partner_id: Optional[int] = None
    reminder_time: Optional[time] = None
    created_at: datetime
    partner: Optional['User'] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PartnerRequestCreate(BaseModel):
    recipient_email: EmailStr

class PartnerRequest(BaseModel):
    id: int
    requester_id: int
    recipient_id: int
    status: str
    created_at: datetime
    requester: User
    recipient: User

    class Config:
        from_attributes = True

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict