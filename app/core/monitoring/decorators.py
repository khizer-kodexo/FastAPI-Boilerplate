import sentry_sdk
from functools import wraps
from typing import Callable, Optional, Any
import inspect

def monitor_transaction(
    name: Optional[str] = None,
    op: Optional[str] = None,
    tags: Optional[dict] = None
):
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
