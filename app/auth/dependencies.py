from fastapi import Depends,Request, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from app.database.connection import db
from app.auth.models import User
from jose import JWTError, jwt
from app.config.settings import settings
from datetime import datetime
from app.utils.logger import logger



# OAuth2PasswordBearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to verify the token and get the user_id
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # Decode the JWT token
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         print(payload)
#         user_id: int = payload.get("sub")  # Assuming the user ID is in the 'sub' claim
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     # Fetch the user from the database
#     user = db["users"].find_one({"id": user_id})
#     if user is None:
#         raise credentials_exception

#     return user

def get_current_user(request: Request):
    logger.info("Inside get_current_user")
    access_token = request.cookies.get("access_token")
    if not access_token:
        print("Access token not found")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode the JWT token
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        print(f"JWT error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch the user from the database
    user =  db["users"].find_one({"email": email})
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user