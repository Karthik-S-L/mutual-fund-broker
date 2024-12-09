from pymongo import MongoClient
from app.config.settings import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.DATABASE_NAME]

try:
    client.admin.command('ping')
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

collections = db.list_collection_names()
print("Collections in database:", collections)

