from pydantic import BaseModel, Field
from typing import List, Dict
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
    funds: List[Fund] = Field(default_factory=list)

class FundFamilyRequest(BaseModel):
    fund_family: str
