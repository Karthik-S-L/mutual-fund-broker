from fastapi import APIRouter, HTTPException, Depends
from app.database.connection import db
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.auth.schemas import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    db.users.insert_one({"email": user.email, "hashed_password": hashed_password})
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    db.users.update_one({"email": user.email}, {"$set": {"refresh_token": refresh_token}})

    return {"access_token": access_token, "refresh_token": refresh_token}
