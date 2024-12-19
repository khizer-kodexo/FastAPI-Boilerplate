from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any

class DatabaseSettings(BaseSettings):
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    MONGODB_TIMEOUT_MS: int = 30000 
    MONGODB_RETRY_WRITES: bool = True
    MONGODB_TLS: bool = True  # Atlas requires TLS
    MONGODB_TLS_CERT_PATH: Optional[str] = None
    MONGODB_AUTH_SOURCE: str = "admin"
    
    @property
    def mongodb_connection_params(self) -> Dict[str, Any]:
        return {
            "minPoolSize": self.MONGODB_MIN_POOL_SIZE,
            "maxPoolSize": self.MONGODB_MAX_POOL_SIZE,
            "timeoutMS": self.MONGODB_TIMEOUT_MS,
            "retryWrites": self.MONGODB_RETRY_WRITES,
            "tls": self.MONGODB_TLS,
            "authSource": self.MONGODB_AUTH_SOURCE
        }

    class Config:
        env_prefix = "DB_"
        extra = "allow"