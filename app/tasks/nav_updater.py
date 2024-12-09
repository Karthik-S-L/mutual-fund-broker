from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.connection import db
from app.config.settings import settings
import httpx

async def update_portfolios():
    """
    Update the current value of investments in all portfolios.
    """
    portfolios = await db["portfolios"].find({}).to_list(None)
    for portfolio in portfolios:
        for fund in portfolio["funds"]:
            url = f"https://{settings.RAPIDAPI_HOST}/mutual-funds"
            headers = {
                "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
                "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            }
            params = {"scheme": fund["scheme_code"]}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                nav = response.json().get("NAV")
                fund["current_value"] = nav * fund["units"]

        await db["portfolios"].update_one({"_id": portfolio["_id"]}, {"$set": {"funds": portfolio["funds"]}})

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_portfolios, "interval", hours=1)
    scheduler.start()
