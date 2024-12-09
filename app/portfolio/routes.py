from fastapi import APIRouter, Depends
from app.database.connection import db
from app.auth.utils import create_access_token

router = APIRouter()

@router.get("/funds")
async def fetch_funds():
    # Implement integration with RapidAPI here
    return {"message": "Funds fetched successfully"}
