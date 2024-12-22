from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.models.domain.profile import ProfileInDB
from app.core.monitoring.decorators import monitor_transaction
from app.core.exceptions import DatabaseException
from app.core.config import settings
from bson import ObjectId

class ProfileRepository:
    def __init__(self, client: "AsyncIOMotorClient"):
        self.client: "AsyncIOMotorClient" = client
        self.database: "AsyncIOMotorDatabase" = client[settings.db.MONGODB_DB_NAME]
        self.collection: "AsyncIOMotorCollection" = self.database["profiles"]

    @monitor_transaction(op="db.profile.create")
    async def create(self, profile: ProfileInDB) -> ProfileInDB:
        try:
            result = await self.collection.insert_one(profile.dict(exclude={"id"}))
            profile.id = str(result.inserted_id)
            return profile
        except Exception as e:
            raise DatabaseException(f"Failed to create profile: {str(e)}")

    @monitor_transaction(op="db.profile.get_by_user_id")
    async def get_by_user_id(self, user_id: str) -> Optional[ProfileInDB]:
        try:
            profile_data = await self.collection.find_one({"user_id": user_id})
            return ProfileInDB(**profile_data) if profile_data else None
        except Exception as e:
            raise DatabaseException(f"Failed to get profile by user_id: {str(e)}")