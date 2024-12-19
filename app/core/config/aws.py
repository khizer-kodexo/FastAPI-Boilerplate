from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any

class AWSSettings(BaseSettings):
    # General AWS Settings
    ENABLED: bool = False
    REGION: str = "us-east-1"
    ACCESS_KEY_ID: Optional[str] = None
    SECRET_ACCESS_KEY: Optional[str] = None
    SESSION_TOKEN: Optional[str] = None
    
    # S3 Settings
    S3_BUCKET_NAME: Optional[str] = None
    S3_PREFIX: str = ""
    S3_PRESIGNED_URL_EXPIRY: int = 3600  # 1 hour
    S3_ACL: str = "private"
    
    # CloudWatch Settings
    CLOUDWATCH_ENABLED: bool = False
    CLOUDWATCH_LOG_GROUP: Optional[str] = None
    CLOUDWATCH_LOG_STREAM_PREFIX: str = ""