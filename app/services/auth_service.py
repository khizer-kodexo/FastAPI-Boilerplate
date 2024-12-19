from datetime import datetime
from typing import Tuple, Optional
from app.models.domain.user import UserCreate, UserInDB, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.security.security import get_password_hash, verify_password
from app.core.security.security import create_access_token, create_refresh_token, verify_token
from app.core.exceptions import (
    ValidationException,
    UnauthorizedException,
    ConflictException,
    ErrorDetail
)
from app.core.monitoring.decorators import monitor_transaction
import sentry_sdk

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @monitor_transaction(op="auth.signup", tags={"service": "auth->signup"})
    async def signup(self, user_data: UserCreate) -> Tuple[UserResponse, str, str]:
        try:
            if not user_data.accept_terms:
                raise ValidationException(
                    message="Terms must be accepted",
                    details=[ErrorDetail(field="accept_terms", message="Terms must be accepted")]
                )

            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ConflictException(
                    message="Email already registered",
                    details=[ErrorDetail(field="email", message="Email already registered")]
                )

            hashed_password = get_password_hash(user_data.password)
            refresh_token, refresh_expires = create_refresh_token()
            
            user = UserInDB(
                **user_data.dict(exclude={"password"}),
                hashed_password=hashed_password,
                refresh_token=refresh_token,
                refresh_token_expires=refresh_expires
            )

            created_user = await self.user_repository.create(user)
            
            access_token = create_access_token({"sub": str(created_user.id)})

            sentry_sdk.add_breadcrumb(
                category="auth",
                message="User created successfully",
                level="info",
                data={"user_id": str(created_user.id)}
            )

            return UserResponse(**created_user.dict()), access_token, refresh_token

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @monitor_transaction(op="auth.refresh_token", tags={"service": "auth->refresh_token"})
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        try:
            user = await self.user_repository.get_by_refresh_token(refresh_token)
            if not user or not user.refresh_token_expires or user.refresh_token_expires < datetime.utcnow():
                raise UnauthorizedException("Invalid or expired refresh token")

            new_refresh_token, refresh_expires = create_refresh_token()
            access_token = create_access_token({"sub": str(user.id)})

            await self.user_repository.update_refresh_token(
                user.id,
                new_refresh_token,
                refresh_expires
            )

            return access_token, new_refresh_token

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise