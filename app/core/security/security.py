from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Any
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
import secrets
from passlib.context import CryptContext

# Create CryptContext once
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token
    
    Args:
        data: Payload to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    return jwt.encode(
        to_encode, 
        settings.security.SECRET_KEY, 
        algorithm=settings.security.ALGORITHM
    )

def create_refresh_token() -> Tuple[str, datetime]:
    """
    Create a new refresh token
    
    Returns:
        Tuple of (token string, expiration datetime)
    """
    token = secrets.token_urlsafe(64)
    expires = datetime.utcnow() + timedelta(days=settings.security.REFRESH_TOKEN_EXPIRE_DAYS)
    return token, expires

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: The token to verify
        
    Returns:
        Decoded payload if valid, None if invalid
        
    Raises:
        JWTError: If token is malformed
        ExpiredSignatureError: If token has expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.security.SECRET_KEY, 
            algorithms=[settings.security.ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except ExpiredSignatureError:
        # Handle expired tokens explicitly
        raise
    except JWTError:
        return None

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)