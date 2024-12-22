from datetime import datetime
from typing import Tuple, Optional
from app.models.domain import UserInDB, UserResponse, SignupRequest, ProfileInDB
from app.repositories import UserRepository, ProfileRepository
from app.core.security.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import (
    UnauthorizedException,
    ConflictException,
    ErrorDetail
)
from app.core.monitoring.decorators import monitor_transaction
import sentry_sdk

class AuthService:
    def __init__(
        self, 
        user_repository: UserRepository,
        profile_repository: ProfileRepository
    ):
        self.user_repository = user_repository
        self.profile_repository = profile_repository

    @monitor_transaction(op="auth.signup", tags={"service": "auth->signup"})
    async def signup(self, signup_data: SignupRequest) -> Tuple[UserResponse, str, str]:
        try:
            existing_user = await self.user_repository.get_by_email(signup_data.email)
            if existing_user:
                raise ConflictException(
                    message="Email already registered",
                    details=[ErrorDetail(field="email", message="Email already registered")]
                )

            hashed_password = get_password_hash(signup_data.password)
            refresh_token, refresh_expires = create_refresh_token()
            
            user = UserInDB(
                email=signup_data.email,
                password=hashed_password,
                refresh_token=refresh_token,
                refresh_token_expires=refresh_expires
            )
            created_user = await self.user_repository.create(user)

            profile = ProfileInDB(
                user_id=created_user.id,
                first_name=signup_data.first_name,
                last_name=signup_data.last_name,
                address_one=signup_data.address_one,
                address_two=signup_data.address_two,
                state=signup_data.state,
                country=signup_data.country,
                phone=signup_data.phone,
                accept_terms=signup_data.accept_terms
            )
            created_profile = await self.profile_repository.create(profile)
            
            access_token = create_access_token({"sub": str(created_user.id)})

            # Combine user and profile data for response
            response_data = {
                **created_user.dict(),
                **created_profile.dict()
            }

            sentry_sdk.add_breadcrumb(
                category="auth",
                message="User created successfully",
                level="info",
                data={"user_id": str(created_user.id)}
            )

            return UserResponse(**response_data), access_token, refresh_token

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    @monitor_transaction(op="auth.refresh_token", tags={"service": "auth->refresh_token"})
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        try:
            user = await self.user_repository.user_by_refresh_token(refresh_token)
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
    
    @monitor_transaction(op="auth.login", tags={"service": "auth->login"})
    async def login(self, email: str, password: str) -> Tuple[str, str]:
        """Login user and return tokens"""
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise UnauthorizedException(
                    message="Invalid credentials",
                    details=[ErrorDetail(field="email", message="Invalid email or password")]
                )

            if not verify_password(password, user.password):
                raise UnauthorizedException(
                    message="Invalid credentials",
                    details=[ErrorDetail(field="password", message="Invalid email or password")]
                )

            await self.user_repository.update_last_login(user.id)
            
            access_token = create_access_token({"sub": str(user.id)})
            refresh_token, refresh_expires = create_refresh_token()
            
            await self.user_repository.update_refresh_token(
                user.id,
                refresh_token,
                refresh_expires
            )

            sentry_sdk.add_breadcrumb(
                category="auth",
                message="User logged in successfully",
                level="info",
                data={"user_id": str(user.id)}
            )

            return access_token, refresh_token

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
