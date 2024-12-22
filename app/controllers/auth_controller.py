from fastapi import Response
from typing import Dict, Any

from app.models.domain import SignupRequest
from app.schemas.auth import UserLogin, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.core.config import settings
from app.core.monitoring.decorators import monitor_transaction

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def set_auth_cookies(self, response: Response, access_token: str, refresh_token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.security.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.security.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.security.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/"
        )

    def clear_auth_cookies(self, response: Response) -> None:
        """Clear authentication cookies"""
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")

    # async def get_current_user(self, token: str):
    #     """Dependency to get current authenticated user"""
    #     try:
    #         payload = decode_access_token(token)
           
    #         user = await self.auth_service.get_user_by_id(payload.get("sub"))
           
    #         return user
    #     except Exception as e:
    #         print(e)

    @monitor_transaction(op="api.auth.register", tags={"endpoint": "auth->register"})
    async def register(self, user_data: SignupRequest, response: Response) -> Dict[str, Any]:
        user, access_token, refresh_token = await self.auth_service.signup(user_data)
        self.set_auth_cookies(response, access_token, refresh_token)
        return {"message": "Registration successful"}

    @monitor_transaction(op="api.auth.login", tags={"endpoint": "auth->login"})
    async def login(self, credentials: UserLogin, response: Response) -> Dict[str, Any]:
        access_token, refresh_token = await self.auth_service.login(
            credentials.email,
            credentials.password
        )
        self.set_auth_cookies(response, access_token, refresh_token)
        return {"message": "Login successful"}

    @monitor_transaction(op="api.auth.refresh", tags={"endpoint": "auth->refresh"})
    async def refresh_token(self, refresh_data: RefreshTokenRequest, response: Response) -> Dict[str, Any]:
        access_token, refresh_token = await self.auth_service.refresh_token(
            refresh_data.refresh_token
        )
        self.set_auth_cookies(response, access_token, refresh_token)
        return {"message": "Token refresh successful"}
