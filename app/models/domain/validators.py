from typing import Optional, Any
from pydantic import field_validator, model_validator
import re
from bson import ObjectId

class PhoneValidatorMixin:
    @field_validator('phone')
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

class PasswordValidatorMixin:
    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '@$!%*#?&^' for c in v):
            raise ValueError('Password must contain at least one special character (@$!%*#?&)')
        return v

class TermsValidatorMixin:
    @model_validator(mode='after')
    def validate_terms(cls, self) -> 'TermsValidatorMixin':
        if not self.accept_terms:
            raise ValueError('Terms must be accepted')
        return self


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> dict:
        """Define the schema used by Pydantic v2."""
        return {
            "type": "string",
            "format": "objectid",
            "validate": cls.validate
        }

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        """Validate and convert input to a valid ObjectId."""
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError(f"Invalid ObjectId: {value}")
