from fastapi import APIRouter,Request, Depends, HTTPException
import httpx
from app.database.connection import db
from app.auth.dependencies import get_current_user
from app.config.settings import settings
from jose import JWTError, jwt
from app.portfolio.models import Fund, Portfolio
from fastapi import HTTPException

router = APIRouter()

"""
    Fetch open-ended schemes for a given fund family.
"""
@router.get("/funds/{fund_family}")
async def get_funds(fund_family: str, user: dict = Depends(get_current_user)):
    url = f"https://{settings.RAPIDAPI_HOST}/mutual-funds"
    headers = {
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
    }
    params = {"family": fund_family, "type": "Open Ended"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(statusCode=response.status_code, detail="Failed to fetch funds")
    funds = response.json()
    return { "statusCode":response.status_code, "message":"Funds fetched successfully", "result":{"fund_family": fund_family, "open_ended_schemes": funds}}


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
    return { "statusCode":response.status_code, "message":"All Funds fetched successfully", "result":response.json() }

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
    return { "statusCode":response.status_code, "message":"", "result":response.json() }  


@router.get("/fund-family/{fund_family}")
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
       "statusCode":response.status_code, 
       "message":"funds successfully fetched",
       "filtered_funds": filtered_funds
    }

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
        db["portfolios"].insert_one(portfolio.model_dump())  # Use .dict() to get a dictionary
    else:
        # portfolio_data needs to be compatible with Portfolio model
        portfolio = Portfolio(**portfolio_data)  # Deserializing the data into a Portfolio model
        portfolio.funds.append(fund)  # Adding the new fund
        db["portfolios"].update_one(
            {"user_id": user_id},
            {"$set": {"funds": [f.model_dump() for f in portfolio.funds]}}  # Using .dict() for serialization
        )

    return {"statusCode":201,"message": "Fund added to portfolio","result":None}

