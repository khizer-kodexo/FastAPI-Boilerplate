from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime

class ErrorCode(str, Enum):
    # Generic Error Codes (1000-1999)
    UNKNOWN_ERROR = "ERR1000"
    VALIDATION_ERROR = "ERR1001"
    RESOURCE_NOT_FOUND = "ERR1002"
    DUPLICATE_RESOURCE = "ERR1003"
    INVALID_REQUEST = "ERR1004"
    
    # Authentication/Authorization Errors (2000-2999)
    UNAUTHORIZED = "ERR2000"
    INVALID_CREDENTIALS = "ERR2001"
    TOKEN_EXPIRED = "ERR2002"
    INVALID_TOKEN = "ERR2003"
    INSUFFICIENT_PERMISSIONS = "ERR2004"
    
    # Database Errors (3000-3999)
    DATABASE_ERROR = "ERR3000"
    CONNECTION_ERROR = "ERR3001"
    QUERY_ERROR = "ERR3002"
    INTEGRITY_ERROR = "ERR3003"
    TRANSACTION_ERROR = "ERR3004"
    
    # External Service Errors (4000-4999)
    SERVICE_UNAVAILABLE = "ERR4000"
    EXTERNAL_API_ERROR = "ERR4001"
    TIMEOUT_ERROR = "ERR4002"
    RATE_LIMIT_EXCEEDED = "ERR4003"
    
    # Business Logic Errors (5000-5999)
    BUSINESS_RULE_VIOLATION = "ERR5000"
    INVALID_STATE = "ERR5001"
    OPERATION_NOT_ALLOWED = "ERR5002"

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = datetime.utcnow().isoformat()
    request_id: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() 
        }

class AppException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []
        self.status_code = status_code
        self.headers = headers or {}
    
    def to_response(self, request_id: Optional[str] = None, path: Optional[str] = None, method: Optional[str] = None) -> ErrorResponse:
        return ErrorResponse(
            code=self.code,
            message=self.message,
            details=self.details,
            request_id=request_id,
            path=path,
            method=method,
            timestamp=datetime.utcnow()
        )