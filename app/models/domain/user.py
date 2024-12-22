from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from .validators import PasswordValidatorMixin

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    email: EmailStr
    status: UserStatus = UserStatus.PENDING
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class UserCreate(UserBase, PasswordValidatorMixin):
    password: str = Field(min_length=8)

class UserInDB(UserBase):
    id: ObjectId = Field(alias='_id', default=None)
    password: str
    verification_token: Optional[str] = None
    refresh_token: Optional[str] = None
    refresh_token_expires: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "populate_by_name": True
    }

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    status: UserStatus
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
    }

