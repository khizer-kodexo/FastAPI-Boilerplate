from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(str, Enum):
    JSON = "json"
    TEXT = "text"

class LoggingSettings(BaseSettings):
    # General Settings
    LEVEL: LogLevel = LogLevel.INFO
    FORMAT: LogFormat = LogFormat.JSON
    
    # File Logging
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_FILE_MAX_SIZE: int = 10485760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    LOG_FILE_ENCODING: str = "utf-8"
    
    # Console Logging
    LOG_TO_CONSOLE: bool = True
    CONSOLE_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Sentry Integration
    SENTRY_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    # ELK Stack Integration
    ELK_ENABLED: bool = False
    ELASTICSEARCH_HOST: Optional[str] = None
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_USERNAME: Optional[str] = None
    ELASTICSEARCH_PASSWORD: Optional[str] = None
    
    # Metrics and Tracing
    ENABLE_METRICS: bool = True
    METRICS_PATH: str = "/metrics"
    ENABLE_TRACING: bool = True
    JAEGER_HOST: Optional[str] = None
    JAEGER_PORT: int = 6831
    
    def get_logging_config(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s"
                },
                "standard": {
                    "format": self.CONSOLE_FORMAT
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if self.FORMAT == LogFormat.JSON else "standard",
                    "level": self.LEVEL.value
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": self.LOG_FILE_PATH,
                    "maxBytes": self.LOG_FILE_MAX_SIZE,
                    "backupCount": self.LOG_FILE_BACKUP_COUNT,
                    "formatter": "json" if self.FORMAT == LogFormat.JSON else "standard",
                    "encoding": self.LOG_FILE_ENCODING
                }
            },
            "root": {
                "level": self.LEVEL.value,
                "handlers": ["console", "file"] if self.LOG_TO_FILE else ["console"]
            }
        }

    class Config:
        env_prefix = "LOG_"
        extra = "allow"