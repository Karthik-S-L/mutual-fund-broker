# models.py in portfolio
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime  


class Fund(BaseModel):
    scheme_code: int
    isin_div_payout_growth: str
    isin_div_reinvestment: str | None = None
    scheme_name: str
    net_asset_value: float
    date: datetime  
    scheme_type: str
    scheme_category: str
    mutual_fund_family: str
    sip: int  
    invested_value:float
    created_at: datetime  
    updated_at: Optional[datetime] 
   
    

class Portfolio(BaseModel):
    user_id: str
    funds: List[Fund]


