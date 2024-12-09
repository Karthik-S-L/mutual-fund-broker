# models.py in portfolio
from pydantic import BaseModel
from typing import List
from datetime import date


class Fund(BaseModel):
    scheme_code: int
    isin_div_payout_growth: str
    isin_div_reinvestment: str | None = None
    scheme_name: str
    net_asset_value: float
    date: date
    scheme_type: str
    scheme_category: str
    mutual_fund_family: str
    

class Portfolio(BaseModel):
    user_id: str
    funds: List[Fund]


