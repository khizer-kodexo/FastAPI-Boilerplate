from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class EmailBackend(str, Enum):
    SMTP = "smtp"
    AMAZON_SES = "ses"
    SENDGRID = "sendgrid"

class EmailSettings(BaseSettings):
    # General Email Settings
    ENABLED: bool = False  # Set default to False
    BACKEND: EmailBackend = EmailBackend.SMTP
    FROM_EMAIL: Optional[str] = None  # Made optional
    FROM_NAME: Optional[str] = None   # Made optional
    REPLY_TO: Optional[str] = None
    
    # SMTP Settings
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    
    # Email Template Settings
    TEMPLATE_DIR: str = "templates/email"
    DEFAULT_TEMPLATE_ENGINE: str = "jinja2"
    
    # Email Limits
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_RECIPIENTS: int = 50

    class Config:
        env_prefix = "EMAIL_"
        extra = "allow"