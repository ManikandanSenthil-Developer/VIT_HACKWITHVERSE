from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# Holding Schemas
class HoldingBase(BaseModel):
    symbol: str
    asset_type: Optional[str] = "Stock"
    quantity: float
    buy_price: float
    current_value: Optional[float] = 0.0
    notes: Optional[str] = None


class HoldingCreate(HoldingBase):
    pass


class HoldingUpdate(BaseModel):
    symbol: Optional[str] = None
    asset_type: Optional[str] = None
    quantity: Optional[float] = None
    buy_price: Optional[float] = None
    current_value: Optional[float] = None
    notes: Optional[str] = None


class HoldingResponse(HoldingBase):
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    cash_balance: Optional[float] = 10000.0
    currency: Optional[str] = "USD"


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cash_balance: Optional[float] = None
    currency: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    total_value: float
    holdings: List[HoldingResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
