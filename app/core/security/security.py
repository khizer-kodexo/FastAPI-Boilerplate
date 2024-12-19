from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from app.core.config import settings
import secrets

def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.security.SECRET_KEY, algorithm=settings.security.ALGORITHM)

def create_refresh_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(64)
    expires = datetime.utcnow() + timedelta(days=settings.security.REFRESH_TOKEN_EXPIRE_DAYS)
    return token, expires

def verify_token(token: str) -> Dict[str, str]:
    try:
        payload = jwt.decode(token, settings.security.SECRET_KEY, algorithms=[settings.security.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_password_hash():
    return

def verify_password():
    return