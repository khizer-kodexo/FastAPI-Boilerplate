from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .validators import PhoneValidatorMixin, TermsValidatorMixin

class ProfileBase(BaseModel, PhoneValidatorMixin, TermsValidatorMixin):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    address_one: str = Field(min_length=5, max_length=100)
    address_two: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None)
    accept_terms: bool = False

class ProfileCreate(ProfileBase):
    user_id: str

class ProfileInDB(ProfileBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {ObjectId: str},
        "from_attributes": True
    }

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    address_one: str
    address_two: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }