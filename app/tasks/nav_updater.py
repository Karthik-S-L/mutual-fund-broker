from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.connection import db
from app.config.settings import settings
import httpx
from app.portfolio.routes import get_all_funds 
from app.utils.logger import logger


async def update_portfolios():
    """
    Update the current value of investments in all portfolios using the available endpoint.
    """
    # Correct way to use await on find() with Motor
    portfolios = await db["portfolios"].find({}).to_list(None)  # Await the cursor properly

    all_funds_response = await get_all_funds() 
    all_funds = all_funds_response.get("result", []) # Ensure this is awaited
    print(all_funds)
    # Log to check all_funds content and portfolio funds
    logger.info(f"Total funds available: {len(all_funds)}")
    logger.info("portfolios",portfolios)
    # for portfolio in portfolios:
    #     for fund in portfolio["funds"]:
    #         # Log the scheme_code for the fund and each fund in all_funds
    #         logger.info(f"Checking for fund scheme_code: {fund['scheme_code']}")

    #         # Match the fund based on the scheme_code
    #         matched_fund = next(
    #             (f for f in all_funds if f.get("scheme_code") == fund["scheme_code"]),  # Use .get() to avoid KeyError
    #             None
    #         )

    #         if matched_fund:
    #             nav = matched_fund["net_asset_value"]
    #             fund["current_value"] = nav * fund["units"]
    #             logger.info(f"Matched fund for scheme_code {fund['scheme_code']} with NAV: {nav}")
    #         else:
    #             logger.warning(f"No match found for scheme_code {fund['scheme_code']}")

    #     # Update the portfolio in the database
    #     await db["portfolios"].update_one(
    #         {"_id": portfolio["_id"]},
    #         {"$set": {"funds": portfolio["funds"]}}
    #     )


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_portfolios, "interval", seconds=10)
    scheduler.start()
