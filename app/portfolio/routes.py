from fastapi import APIRouter,Request, Depends, HTTPException
import httpx
from app.database.connection import db
from app.auth.dependencies import get_current_user
from app.config.settings import settings
from jose import JWTError, jwt
from app.portfolio.models import Fund, Portfolio
from fastapi import HTTPException, status
from app.utils.logger import logger

router = APIRouter()

@router.get("/all-funds")
async def get_all_funds():
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
async def get_master_funds():
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
    logger.info(f"Received input for fund: {fund}")

    """
    Add a fund to the user's portfolio.
    """
    # Ensure user is authenticated
    if not user or "_id" not in user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = str(user["_id"])
    portfolio_data = db["portfolios"].find_one({"user_id": user_id})

    if not portfolio_data:
        # Create a new portfolio
        logger.info("Portfolio does not exist, creating a new one")
        portfolio = Portfolio(user_id=user_id, funds=[fund])
        db["portfolios"].insert_one(portfolio.model_dump())  
    else:
        # Convert database funds into Fund models
        portfolio_data["funds"] = [
            Fund(**f) for f in portfolio_data.get("funds", [])
        ]
        
        # Check if the fund with the same scheme_code already exists
        for existing_fund in portfolio_data["funds"]:
            if existing_fund.scheme_code == fund.scheme_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Fund with scheme_code {fund.scheme_code} already exists in the portfolio"
                )

        # Deserialize the existing portfolio
        portfolio = Portfolio(**portfolio_data)

        # Add the new fund to the portfolio
        portfolio.funds.append(fund)

        # Update the database
        db["portfolios"].update_one(
            {"user_id": user_id},
            {"$set": {"funds": [f.model_dump() for f in portfolio.funds]}}  # Serialize with .model_dump()
        )

    return {"statusCode": 201, "message": "Fund added to portfolio", "result": None}

