# models.py in portfolio
from pydantic import BaseModel
from typing import List


class Fund(BaseModel):
    name: str
    fund_family: str
    scheme_type: str
    nav: float
    units: int
    investment_value: float


class Portfolio(BaseModel):
    user_id: str
    funds: List[Fund]


