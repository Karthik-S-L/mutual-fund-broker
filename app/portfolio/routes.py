from fastapi import APIRouter,Request, Depends, HTTPException
import httpx
from app.database.connection import db
from app.auth.dependencies import get_current_user
from app.config.settings import settings
from jose import JWTError, jwt
from app.portfolio.models import Fund, Portfolio





router = APIRouter()

@router.get("/funds/{fund_family}")
async def get_funds(fund_family: str, user: dict = Depends(get_current_user)):
    """
    Fetch open-ended schemes for a given fund family.
    """

    url = f"https://{settings.RAPIDAPI_HOST}/mutual-funds"
    headers = {
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
    }
    params = {"family": fund_family, "type": "Open Ended"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch funds")

    funds = response.json()
    return {"fund_family": fund_family, "open_ended_schemes": funds}




@router.get("/all-funds")
async def get_funds():
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"
    querystring = {"Scheme_Type": "Open"}
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "latest-mutual-fund-nav.p.rapidapi.com"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=querystring)
    return response.json()  

@router.get("/master")
async def get_funds():
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/master"
    querystring = {"RTA_Agent_Code":"CAMS"}
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "latest-mutual-fund-nav.p.rapidapi.com"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=querystring)
    return response.json()  


from pydantic import BaseModel
from fastapi import HTTPException

# Define a Pydantic model for the request body
class FundFamilyRequest(BaseModel):
    fund_family: str

@router.get("/funds3/{fund_family}")
async def get_funds_by_family(fund_family: str):
    """
    Fetch mutual funds filtered by a specific fund family.
    """
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"
    querystring = {"Scheme_Type": "Open"}

    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "latest-mutual-fund-nav.p.rapidapi.com"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch mutual funds"
        )

    all_funds = response.json()

    # Filter funds based on the provided fund family
    filtered_funds = [
        fund for fund in all_funds
        if fund["Mutual_Fund_Family"].strip().lower() == fund_family.strip().lower()
    ]

    return {
       
        "filtered_funds": filtered_funds
    }

def get_current_user(request: Request):
    print("Inside get_current_user")

    # Log all cookies for debugging
    print(f"Cookies: {request.cookies}")

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
        print(f"Decoded payload: {payload}")
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
    user = db["users"].find_one({"email": email})
    print(f"Fetched user: {user}")
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

@router.post("/")
async def add_to_portfolio(fund: Fund, user: dict = Depends(get_current_user)):
    """
    Add a mutual fund to the user's portfolio.
    """
    # Ensure user is authenticated
    if not user or "_id" not in user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the user's portfolio or create a new one
    user_id = str(user["_id"])
    portfolio_data =  db["portfolios"].find_one({"user_id": user_id})

    if not portfolio_data:
        portfolio = Portfolio(user_id=user_id, funds=[fund])
        db["portfolios"].insert_one(portfolio.dict())  # Use .dict() to get a dictionary
    else:
        # portfolio_data needs to be compatible with Portfolio model
        portfolio = Portfolio(**portfolio_data)  # Deserializing the data into a Portfolio model
        portfolio.funds.append(fund)  # Adding the new fund
        db["portfolios"].update_one(
            {"user_id": user_id},
            {"$set": {"funds": [f.dict() for f in portfolio.funds]}}  # Using .dict() for serialization
        )

    return {"message": "Fund added to portfolio"}

