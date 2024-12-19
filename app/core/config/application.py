from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ApplicationSettings(BaseSettings):
    # Basic Application Settings
    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-grade FastAPI boilerplate with MongoDB"
    API_V1_STR: str = "/api/v1"
    
    # Environment Settings
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    DEBUG: bool = False
    TESTING: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS_COUNT: int = 4
    RELOAD: bool = False
    
    # CORS Settings (TODO: add only allowed ones)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"] 
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    RATE_LIMIT_ENABLED: bool = True
    
    # Documentation Settings
    DOCS_URL: str = "/api/docs"
    REDOC_URL: str = "/api/redoc"
    OPENAPI_URL: str = "/api/openapi.json"
    
    # Middleware Settings
    MIDDLEWARE_GZIP_MINIMUM_SIZE: int = 1000
    MIDDLEWARE_TIMEOUT: int = 60

    class Config:
        env_prefix = "APP_"
        extra = "allow"