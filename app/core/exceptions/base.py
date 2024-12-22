from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    status_code: int
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
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or []
        self.status_code = status_code
        self.headers = headers or {}
    
    def to_response(self, request_id: Optional[str] = None, path: Optional[str] = None, method: Optional[str] = None) -> ErrorResponse:
        return ErrorResponse(
            status_code = self.status_code,
            message=self.message,
            details=self.details,
            request_id=request_id,
            path=path,
            method=method,
            timestamp=datetime.utcnow()
        )