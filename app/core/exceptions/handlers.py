from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Type
from .base import AppException, ErrorResponse, ErrorCode, ErrorDetail
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    error_response = exc.to_response(
        request_id=request.state.request_id,
        path=request.url.path,
        method=request.method
    )
    
    logger.error(
        f"Application error occurred: {error_response.json()}",
        extra={
            "request_id": request.state.request_id,
            "error_code": exc.code,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.json(),
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            code="VALIDATION_ERROR"
        )
        for error in exc.errors()
    ]
    
    error_response = ErrorResponse(
        code=ErrorCode.VALIDATION_ERROR,
        message="Validation error",
        details=details,
        request_id=request.state.request_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict(),
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    error_response = ErrorResponse(
        code=ErrorCode.UNKNOWN_ERROR,
        message=str(exc.detail),
        request_id=request.state.request_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=getattr(exc, "headers", None)
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions"""
    error_response = ErrorResponse(
        code=ErrorCode.UNKNOWN_ERROR,
        message="An unexpected error occurred",
        request_id=request.state.request_id,
        path=request.url.path,
        method=request.method
    )
    
    logger.error(
        "Unhandled exception occurred",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": "".join(traceback.format_exception(*sys.exc_info()))
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the application"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


# Example usage in your routes:
# @router.get("/items/{item_id}")
# async def get_item(item_id: str):
#     try:
#         item = await item_service.get_item(item_id)
#         if not item:
#             raise NotFoundException(f"Item with id {item_id} not found")
#         return item
#     except DatabaseException as e:
#         raise ServiceException(
#             message="Failed to retrieve item",
#             details=[ErrorDetail(message=str(e))]
#         )