from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings

client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client
    client = AsyncIOMotorClient(settings.mongodb_url)
    print(f"Connected to MongoDB at {settings.mongodb_url}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database():
    """Get database instance"""
    return client[settings.database_name]
