from typing import Optional, List, Dict
from .base import AppException, ErrorCode, ErrorDetail

class ServiceException(AppException):
    def __init__(
        self,
        code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE,
        message: str = "Service error occurred",
        details: Optional[List[ErrorDetail]] = None,
        status_code: int = 503,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=status_code,
            headers=headers
        )

class ExternalServiceException(ServiceException):
    def __init__(
        self,
        message: str = "External service error",
        details: Optional[List[ErrorDetail]] = None,
        service_name: Optional[str] = None
    ):
        if service_name:
            message = f"{service_name}: {message}"
        super().__init__(
            code=ErrorCode.EXTERNAL_API_ERROR,
            message=message,
            details=details
        )
