from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.models.domain.user import UserInDB
from app.core.monitoring.decorators import monitor_transaction
from app.core.exceptions import DatabaseException, NotFoundException
from app.core.config import settings
from bson import ObjectId
class UserRepository:
    def __init__(self, client: "AsyncIOMotorClient"):
        self.client: "AsyncIOMotorClient" = client
        self.database: "AsyncIOMotorDatabase" = client[settings.db.MONGODB_DB_NAME]
        self.collection: "AsyncIOMotorCollection" = self.database["users"]

    @monitor_transaction(op="db.user.create")
    async def create(self, user: UserInDB) -> UserInDB:
        try:
            result = await self.collection.insert_one(user.dict())
            user.id = str(result.inserted_id)
            return user
        except Exception as e:
            raise DatabaseException(f"Failed to create user: {str(e)}")

    @monitor_transaction(op="db.user.get_by_email")
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        try:
            user_data = await self.collection.find_one({"email": email})
            return UserInDB(**user_data) if user_data else None
        except Exception as e:
            raise DatabaseException(f"Failed to get user by email: {str(e)}")

    @monitor_transaction(op="db.user.get_by_refresh_token")
    async def user_by_refresh_token(self, refresh_token: str) -> Optional[UserInDB]:
        try:
            user_data = await self.collection.find_one({"refresh_token": refresh_token})
            return UserInDB(**user_data) if user_data else None
        except Exception as e:
            raise DatabaseException(f"Failed to get user by refresh token: {str(e)}")

    @monitor_transaction(op="db.user.update_refresh_token")
    async def update_refresh_token(
        self, 
        user_id: str, 
        refresh_token: Optional[str], 
        expires: Optional[datetime]
    ) -> None:
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            print("--USER--", user, user_id)
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "refresh_token": refresh_token,
                        "refresh_token_expires": expires,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            raise DatabaseException(f"Failed to update refresh token: {str(e)}")

    @monitor_transaction(op="db.user.update_last_login")
    async def update_last_login(self, user_id: str) -> None:
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            raise DatabaseException(f"Failed to update last login: {str(e)}")