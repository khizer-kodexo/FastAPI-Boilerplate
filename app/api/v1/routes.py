from fastapi import APIRouter
from app.repositories import UserRepository, ProfileRepository
from app.services.auth_service import AuthService
from .endpoints.auth import AuthRouter
from app.core.db import mongodb

def create_api_router() -> APIRouter:
    api_router = APIRouter()
    
    user_repository = UserRepository(mongodb.client)
    profile_repository = ProfileRepository(mongodb.client)

    auth_service = AuthService(user_repository, profile_repository)
    
    auth_router = AuthRouter(auth_service)
    
    api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
    
    return api_router