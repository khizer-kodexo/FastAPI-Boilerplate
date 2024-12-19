from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    first_name: constr(min_length=2, max_length=50)
    last_name: constr(min_length=2, max_length=50)
    email: EmailStr
    address_one: constr(min_length=5, max_length=100)
    address_two: Optional[constr(max_length=100)] = None
    state: Optional[constr(max_length=50)] = None
    country: Optional[constr(max_length=50)] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    accept_terms: bool = False

class UserCreate(UserBase):
    password: constr(min_length=8, regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$')

class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    hashed_password: str
    status: UserStatus = UserStatus.PENDING
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    verification_token: Optional[str] = None
    refresh_token: Optional[str] = None
    refresh_token_expires: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str
    status: UserStatus
    email_verified: bool
    created_at: datetime
    updated_at: datetime