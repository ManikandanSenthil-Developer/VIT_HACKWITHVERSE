from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WatchlistBase(BaseModel):
    name: str
    description: Optional[str] = None
    symbols: Optional[str] = "AAPL,NVDA,MSFT,TSLA,AMZN"


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symbols: Optional[str] = None


class WatchlistResponse(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
