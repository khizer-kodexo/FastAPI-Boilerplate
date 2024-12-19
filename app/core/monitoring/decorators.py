import sentry_sdk
from functools import wraps
from typing import Callable, Optional, Any
import inspect

def monitor_transaction(
    name: Optional[str] = None,
    op: Optional[str] = None,
    tags: Optional[dict] = None
):
    """Decorator to monitor function execution in Sentry"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            transaction_name = name or f"{func.__module__}.{func.__name__}"
            with sentry_sdk.start_transaction(
                name=transaction_name,
                op=op or "function"
            ) as transaction:
                if tags:
                    for key, value in tags.items():
                        transaction.set_tag(key, value)
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            transaction_name = name or f"{func.__module__}.{func.__name__}"
            with sentry_sdk.start_transaction(
                name=transaction_name,
                op=op or "function"
            ) as transaction:
                if tags:
                    for key, value in tags.items():
                        transaction.set_tag(key, value)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    raise

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Example implementation
# from fastapi import FastAPI
# from .core.monitoring import get_sentry_service, SentryContextMiddleware
# from .core.config import settings

# def create_app() -> FastAPI:
#     app = FastAPI()
    
#     # Initialize Sentry if enabled
#     if settings.logging.SENTRY_ENABLED:
#         sentry_service = get_sentry_service()
#         sentry_service.initialize()
        
#         # Add Sentry context middleware
#         app.add_middleware(SentryContextMiddleware)
    
#     return app

# # Example usage in a service
# from .core.monitoring.decorators import monitor_transaction

# class UserService:
#     @monitor_transaction(op="user.create", tags={"service": "user"})
#     async def create_user(self, user_data: dict) -> User:
#         try:
#             # Your user creation logic here
#             user = await self.user_repository.create(user_data)
#             return user
#         except Exception as e:
#             # Sentry will automatically capture this exception
#             raise

# # Example usage in an endpoint
# @router.post("/users/")
# @monitor_transaction(op="http.request", tags={"endpoint": "create_user"})
# async def create_user(user_data: UserCreate):
#     try:
#         return await user_service.create_user(user_data)
#     except Exception as e:
#         # The exception will be automatically captured by Sentry
#         raise