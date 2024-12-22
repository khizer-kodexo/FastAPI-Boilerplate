from fastapi import APIRouter, status

from app.schemas.auth import TokenResponse
from app.services.auth_service import AuthService
from app.controllers.auth_controller import AuthController

class AuthRouter:
    def __init__(self, auth_service: AuthService):
        self.controller = AuthController(auth_service)
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        self.router.add_api_route(
            "/register",
            self.controller.register,
            methods=["POST"],
            response_model=TokenResponse,
            status_code=status.HTTP_201_CREATED
        )
        self.router.add_api_route(
            "/login",
            self.controller.login,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.router.add_api_route(
            "/refresh",
            self.controller.refresh_token,
            methods=["POST"],
            response_model=TokenResponse
        )
