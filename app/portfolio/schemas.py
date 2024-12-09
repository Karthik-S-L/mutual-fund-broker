from pydantic import BaseModel, Field
from typing import List, Dict

class Fund(BaseModel):
    name: str
    fund_family: str
    scheme_type: str
    nav: float
    units: int
    investment_value: float

class Portfolio(BaseModel):
    user_id: str
    funds: List[Fund] = Field(default_factory=list)
