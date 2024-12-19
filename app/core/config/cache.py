from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class CacheBackend(str, Enum):
    REDIS = "redis"
    MEMCACHED = "memcached"
    IN_MEMORY = "memory"

class CacheSettings(BaseSettings):
    # General Cache Settings
    ENABLED: bool = True
    BACKEND: CacheBackend = CacheBackend.REDIS
    KEY_PREFIX: str = "fastapi_cache"
    DEFAULT_TIMEOUT: int = 300  # 5 minutes
    
    # Redis Settings
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_POOL_MIN_SIZE: int = 1
    REDIS_POOL_MAX_SIZE: int = 10
    
    # Memcached Settings
    MEMCACHED_HOSTS: List[str] = ["localhost:11211"]
    MEMCACHED_POOL_SIZE: int = 10
    
    # Cache Keys Settings
    CACHE_KEY_SEPARATOR: str = ":"
    CACHE_NONE_TIMEOUT: int = 5  # Timeout for None values
    
    # Serialization
    SERIALIZER: str = "json"  # or "pickle"
    COMPRESSION_ENABLED: bool = True
    COMPRESSION_THRESHOLD: int = 1000  # bytes
    
    # Cache Patterns
    PATTERN_CACHE_ENABLED: bool = True
    PATTERN_CACHE_TIMEOUT: int = 3600  # 1 hour
    
    class Config:
        env_prefix = "CACHE_"
        extra = "allow"
