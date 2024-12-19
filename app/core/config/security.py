from pydantic_settings import BaseSettings
from typing import Optional, List
from datetime import timedelta

class SecuritySettings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 50
    PASSWORD_REGEX: str = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    
    # Authentication Settings
    AUTH_HEADER_NAME: str = "Authorization"
    AUTH_TOKEN_PREFIX: str = "Bearer"
    AUTH_COOKIE_NAME: str = "access_token"
    AUTH_COOKIE_DOMAIN: Optional[str] = None
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_SAMESITE: str = "lax"
    
    # API Key Settings
    API_KEY_HEADER_NAME: str = "X-API-Key"
    API_KEY_ENABLED: bool = True
    
    # CSRF Protection
    CSRF_ENABLED: bool = True
    CSRF_TOKEN_LENGTH: int = 32
    CSRF_COOKIE_NAME: str = "csrf_token"
    
    # Security Headers
    SECURITY_HEADERS: bool = True
    HSTS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000
    CSP_ENABLED: bool = True
    CSP_POLICY: str = "default-src 'self'"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE: str = "memory"  # or "redis"
    
    # IP Filtering
    IP_WHITELIST: List[str] = []
    IP_BLACKLIST: List[str] = []
    
    @property
    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def refresh_token_expires(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    class Config:
        env_prefix = "SECURITY_"
        extra = "allow"