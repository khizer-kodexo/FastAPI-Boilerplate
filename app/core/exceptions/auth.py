from typing import Optional, List, Dict
from .base import AppException, ErrorDetail
from http import HTTPStatus

class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            details=details,
            status_code=HTTPStatus.NON_AUTHORITATIVE_INFORMATION,
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )

class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            details=details,
            status_code=HTTPStatus.UNAUTHORIZED,
            headers=headers
        )
