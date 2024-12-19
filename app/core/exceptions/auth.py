from typing import Optional, List, Dict
from .base import AppException, ErrorCode, ErrorDetail

class AuthenticationException(AppException):
    def __init__(
        self,
        code: ErrorCode = ErrorCode.INVALID_CREDENTIALS,
        message: str = "Authentication failed",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=401,
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )

class AuthorizationException(AppException):
    def __init__(
        self,
        code: ErrorCode = ErrorCode.INSUFFICIENT_PERMISSIONS,
        message: str = "Insufficient permissions",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=403,
            headers=headers
        )
