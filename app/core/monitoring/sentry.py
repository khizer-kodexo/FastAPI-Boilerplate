import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.scrubber import EventScrubber
from functools import lru_cache
from typing import Optional, List, Dict, Any, Set
import logging
import re
from ..config import settings

logger = logging.getLogger(__name__)

class SentryConfig:
    def __init__(
        self,
        dsn: str,
        environment: str,
        release: Optional[str] = None,
        traces_sample_rate: float = 1.0,
        profiles_sample_rate: float = 1.0,
        max_breadcrumbs: int = 100,
        attach_stacktrace: bool = True,
        send_default_pii: bool = False,
        server_name: Optional[str] = None,
        sensitive_fields: Set[str] = None,
        ignore_errors: List[type] = None,
        custom_tags: Dict[str, str] = None
    ):
        self.dsn = dsn
        self.environment = environment
        self.release = release
        self.traces_sample_rate = traces_sample_rate
        self.profiles_sample_rate = profiles_sample_rate
        self.max_breadcrumbs = max_breadcrumbs
        self.attach_stacktrace = attach_stacktrace
        self.send_default_pii = send_default_pii
        self.server_name = server_name
        self.sensitive_fields = sensitive_fields or {
            "password", "secret", "token", "api_key", "access_key",
            "credit_card", "card_number", "auth", "credentials"
        }
        self.ignore_errors = ignore_errors or []
        self.custom_tags = custom_tags or {}

class CustomEventScrubber(EventScrubber):
    """Custom event scrubber to handle sensitive data"""
    
    def __init__(self, sensitive_fields: Set[str]):
        super().__init__()
        self.sensitive_fields = sensitive_fields
        self.sensitive_pattern = re.compile(
            '|'.join(f'(?i){field}' for field in sensitive_fields)
        )

    def scrub_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub sensitive data from the event payload"""
        if not isinstance(data, dict):
            return data

        scrubbed_data = data.copy()
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                scrubbed_data[key] = self.scrub_data(value)
            elif isinstance(key, str) and self.sensitive_pattern.search(key):
                scrubbed_data[key] = "[Filtered]"
            elif isinstance(value, str) and any(
                field in value.lower() for field in self.sensitive_fields
            ):
                scrubbed_data[key] = "[Filtered]"
        return scrubbed_data

class SentryService:
    """Service for managing Sentry integration"""

    def __init__(self, config: SentryConfig):
        self.config = config
        self._initialized = False

    def initialize(self) -> None:
        """Initialize Sentry SDK with configurations"""
        if self._initialized:
            logger.warning("Sentry is already initialized")
            return

        try:
            sentry_sdk.init(
                dsn=self.config.dsn,
                environment=self.config.environment,
                release=self.config.release,
                traces_sample_rate=self.config.traces_sample_rate,
                profiles_sample_rate=self.config.profiles_sample_rate,
                max_breadcrumbs=self.config.max_breadcrumbs,
                attach_stacktrace=self.config.attach_stacktrace,
                send_default_pii=self.config.send_default_pii,
                server_name=self.config.server_name,
                before_send=self._before_send,
                before_breadcrumb=self._before_breadcrumb,
                integrations=self._get_integrations(),
                event_scrubber=CustomEventScrubber(self.config.sensitive_fields)
            )

            # Set global tags
            for key, value in self.config.custom_tags.items():
                sentry_sdk.set_tag(key, value)

            self._initialized = True
            logger.info(
                "Sentry initialized successfully",
                extra={
                    "environment": self.config.environment,
                    "release": self.config.release
                }
            )

        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {str(e)}", exc_info=True)
            raise

    def _get_integrations(self) -> List[Any]:
        """Get list of Sentry integrations"""
        return [
            FastApiIntegration(transaction_style="url"),
            AsyncioIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
            StdlibIntegration()
        ]

    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event before sending to Sentry"""
        # Check if error should be ignored
        if hint.get("exc_info"):
            exc_type, _, _ = hint["exc_info"]
            if exc_type in self.config.ignore_errors:
                return None

        # Add custom context
        event.setdefault("contexts", {}).update({
            "app_info": {
                "name": settings.app.PROJECT_NAME,
                "version": settings.app.VERSION
            }
        })

        return event

    def _before_breadcrumb(self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process breadcrumb before adding to event"""
        # Filter out sensitive data from breadcrumbs
        if "data" in breadcrumb:
            breadcrumb["data"] = self._filter_sensitive_data(breadcrumb["data"])
        return breadcrumb

    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from dictionary"""
        if isinstance(data, dict):
            return {
                key: "[Filtered]" if any(
                    field in key.lower() for field in self.config.sensitive_fields
                ) else (
                    self._filter_sensitive_data(value)
                    if isinstance(value, (dict, list)) else value
                )
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item) for item in data]
        return data

@lru_cache
def get_sentry_service() -> SentryService:
    """Get or create Sentry service instance"""
    config = SentryConfig(
        dsn=settings.logging.SENTRY_DSN,
        environment=settings.logging.SENTRY_ENVIRONMENT,
        release=f"{settings.app.PROJECT_NAME}@{settings.app.VERSION}",
        traces_sample_rate=settings.logging.SENTRY_TRACES_SAMPLE_RATE,
        custom_tags={
            "app_name": settings.app.PROJECT_NAME,
            "app_version": settings.app.VERSION
        }
    )
    return SentryService(config)