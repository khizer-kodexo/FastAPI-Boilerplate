from .application import ApplicationSettings
from .database import DatabaseSettings
from .security import SecuritySettings
from .logging import LoggingSettings
from .cache import CacheSettings
from .email import EmailSettings
from .aws import AWSSettings
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Any, Dict, List

class Settings(BaseSettings):
    app: ApplicationSettings = ApplicationSettings()
    db: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    cache: CacheSettings = CacheSettings()
    email: EmailSettings = EmailSettings()
    aws: AWSSettings = AWSSettings()

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        extra = "allow"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()