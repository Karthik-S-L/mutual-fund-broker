from fastapi import APIRouter,Request, Depends, HTTPException
import httpx
from app.database.connection import db
from app.auth.dependencies import get_current_user
from app.config.settings import settings
from jose import JWTError, jwt
from app.portfolio.models import Fund, Portfolio
from fastapi import HTTPException, status
from app.portfolio.schemas import FundSchema
from app.utils.logger import logger
from datetime import datetime, timedelta, timezone
from pymongo import ReturnDocument

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
async def add_to_portfolio(fund: FundSchema, user: dict = Depends(get_current_user)):
    logger.info(f"Received input for fund: {fund}")

    # Ensure user is authenticated
    if not user or "_id" not in user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = str(user["_id"])
    portfolio_data = db["portfolios"].find_one({"user_id": user_id})
    current_time = datetime.now(timezone.utc)

    if not portfolio_data:
        logger.info("Portfolio does not exist, creating a new one")
        # Generate dictionary from input schema and remove fields to avoid conflicts
        fund_data = fund.model_dump()
        fund_data.pop("sip", None)
        fund_data.pop("created_at", None)
        fund_data.pop("updated_at", None)
        fund_data.pop("invested_value",None)

        # Create the Fund model with additional fields
        new_fund = Fund(
            **fund_data,
            sip=1,
            invested_value=fund.net_asset_value,
            created_at=current_time,
            updated_at=current_time,
        )

        portfolio = Portfolio(user_id=user_id, funds=[new_fund])
        
        db["portfolios"].insert_one(portfolio.model_dump())
    else:
        # Handle existing portfolio
        for existing_fund in portfolio_data.get("funds", []):
            if existing_fund["scheme_code"] == fund.scheme_code:
                db["portfolios"].find_one_and_update(
                    {"user_id": user_id, "funds.scheme_code": fund.scheme_code},
                    {
                        "$inc": {"funds.$.sip": 1,"funds.$.invested_value":fund.net_asset_value},
                        "$set": {"funds.$.updated_at": current_time},
                    },
                )
                return {
                    "statusCode": 200,
                    "message": f"SIP incremented for fund with scheme_code {fund.scheme_code}",
                    "result": None,
                }

        new_fund = Fund(
            **fund.dict(),
            sip=1,
            created_at=current_time,
            updated_at=current_time,
        )
        portfolio_data["funds"].append(new_fund.model_dump())
        db["portfolios"].update_one(
            {"user_id": user_id},
            {"$set": {"funds": portfolio_data["funds"]}},
        )

    return {"statusCode": 201, "message": "Fund added to portfolio", "result": None}

@router.get("/")
async def view_portfolio(user: dict = Depends(get_current_user)):
    logger.info("Inside view_portfolio")
    # Ensure user is authenticated
    if not user or "_id" not in user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = str(user["_id"])

    # Fetch the user's portfolio from the database
    portfolio_data = db["portfolios"].find_one({"user_id": user_id})

    if not portfolio_data:
        return {
            "statusCode": 404,
            "message": "Portfolio not found",
            "result": None,
        }

    current_time = datetime.utcnow()
    updated_funds = []

    for fund in portfolio_data["funds"]:
        updated_at = fund.get("updated_at")

        if updated_at:
            if isinstance(updated_at, str):
                try:
                    print("daffafafafaf")
                    # Replace space with T and convert to datetime
                    updated_at = datetime.fromisoformat(updated_at.replace(" ", "T"))
                except ValueError:
                    logger.warning(f"Invalid updated_at format for fund: {fund['scheme_code']}")
                    updated_at = None
            elif isinstance(updated_at, datetime):
                pass
            else:
                updated_at = None

        # If updated_at is more than an hour ago or not present, fetch the latest NAV
        if not updated_at or (current_time - updated_at > timedelta(hours=1)):
            scheme_code = fund["scheme_code"]
            latest_navs = await fetch_latest_nav([scheme_code])
            if scheme_code in latest_navs:
                fund["net_asset_value"] = latest_navs[scheme_code]
            else:
                logger.warning(f"Keeping current NAV for scheme_code: {scheme_code}")
            fund["updated_at"] = current_time.isoformat()

        updated_funds.append(fund)

    # Update the portfolio in the database
    db["portfolios"].update_one(
        {"user_id": user_id},
        {"$set": {"funds": updated_funds}}
    )

    return {
        "statusCode": 200,
        "message": "Portfolio fetched successfully",
        "result": updated_funds,
    }


#Fetch the latest NAV for a list of scheme codes.
async def fetch_latest_nav(scheme_codes: list[int]) -> dict[int, float]:
    logger.info("Inside fetch_latest_nav")
    try:
        all_funds_response = await get_all_funds()
        if "result" not in all_funds_response:
            logger.error("Response does not contain 'result' key.")
            return {}  # Return an empty dictionary or handle the error appropriately
    except Exception as e:
        logger.error(f"Error fetching funds data: {e}")
        return {}
    all_funds = all_funds_response["result"]

    if not all(isinstance(fund, dict) and "Scheme_Code" in fund and "Net_Asset_Value" in fund for fund in all_funds):
        logger.error(f"Expected list of dictionaries with keys 'Scheme_Code' and 'Net_Asset_Value', but got {type(all_funds)}: {all_funds}")
        return {}

    nav_mapping = {fund["Scheme_Code"]: fund["Net_Asset_Value"] for fund in all_funds}
    
    latest_nav = {}
    for scheme_code in scheme_codes:
        if scheme_code in nav_mapping:
            latest_nav[scheme_code] = nav_mapping[scheme_code]
        else:
            logger.warning(f"Failed to get latest NAV for scheme_code: {scheme_code}")

    if not latest_nav:
        logger.warning("No NAVs were found for the provided scheme codes.")

    return latest_nav

    

 