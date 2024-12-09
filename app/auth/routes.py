from fastapi import APIRouter, Response,HTTPException, Depends
from app.auth.dependencies import get_current_user
from app.database.connection import db
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.auth.schemas import UserCreate, UserLogin
from datetime import timedelta

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
async def login(user: UserLogin, response:Response):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access and refresh tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    # Store the refresh token in the database
    db.users.update_one({"email": user.email}, {"$set": {"refresh_token": refresh_token}})

    # Set the access token in an HTTP-only cookie for security
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=timedelta(hours=1),  # set an expiration time as per your requirements
        httponly=True,  # This ensures the cookie is not accessible via JavaScript
        secure=True,  # Use secure cookies (only over HTTPS)
        samesite="Strict"  # Helps prevent CSRF attacks
    )
    
    # You can also send the refresh token in response body or store it in cookies if needed
    return {"refresh_token": refresh_token}

@router.get("/me",)
async def get_user(user = Depends(get_current_user)):
    return user
