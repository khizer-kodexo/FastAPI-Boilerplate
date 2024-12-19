from typing import Optional, List, Dict
from .base import AppException, ErrorCode, ErrorDetail

class DatabaseException(AppException):
    def __init__(
        self,
        code: ErrorCode = ErrorCode.DATABASE_ERROR,
        message: str = "Database error occurred",
        details: Optional[List[ErrorDetail]] = None,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=status_code,
            headers=headers
        )

class ConnectionException(DatabaseException):
    def __init__(
        self,
        message: str = "Database connection error",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            code=ErrorCode.CONNECTION_ERROR,
            message=message,
            details=details
        )

class QueryException(DatabaseException):
    def __init__(
        self,
        message: str = "Database query error",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            code=ErrorCode.QUERY_ERROR,
            message=message,
            details=details
        )
