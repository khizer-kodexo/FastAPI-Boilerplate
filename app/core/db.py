from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConnector:
    client: Optional[AsyncIOMotorClient] = None

    async def connect_to_mongodb(self, db_url: str, **kwargs):
        logger.info("Connecting to MongoDB...")
        try:
            self.client = AsyncIOMotorClient(db_url, **kwargs)
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    async def close_mongodb_connection(self):
        logger.info("Closing MongoDB connection...")
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

mongodb = MongoDBConnector()