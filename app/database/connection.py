from pymongo import MongoClient
from app.config.settings import settings
from app.utils.logger import logger

from motor.motor_asyncio import AsyncIOMotorClient

# Make sure you're using the correct async client (motor)
# client = AsyncIOMotorClient(settings.MONGO_URI)
# db = client[settings.DATABASE_NAME]

client = MongoClient(settings.MONGO_URI)
db = client[settings.DATABASE_NAME]

try:
    client.admin.command('ping')
    logger.info("MongoDB connection successful")
except Exception as e:
     logger.info(f"MongoDB connection failed: {e}")



