from typing import Optional, List, Dict
from .base import AppException, ErrorCode, ErrorDetail

class HTTPException(AppException):
    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=status_code,
            headers=headers
        )

class BadRequestException(HTTPException):
    def __init__(
        self,
        message: str = "Invalid request",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=400,
            code=ErrorCode.INVALID_REQUEST,
            message=message,
            details=details,
            headers=headers
        )

class UnauthorizedException(HTTPException):
    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        if not headers:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=401,
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
            headers=headers
        )

class ForbiddenException(HTTPException):
    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=403,
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
            details=details,
            headers=headers
        )

class NotFoundException(HTTPException):
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=404,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            details=details,
            headers=headers
        )

class ConflictException(HTTPException):
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=409,
            code=ErrorCode.DUPLICATE_RESOURCE,
            message=message,
            details=details,
            headers=headers
        )

class ValidationException(HTTPException):
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=422,
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            headers=headers
        )

class RateLimitException(HTTPException):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=429,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            details=details,
            headers=headers
        )