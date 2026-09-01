from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InvestorProfileBase(BaseModel):
    risk_tolerance: Optional[str] = "moderate"
    investment_horizon: Optional[str] = "medium"
    preferred_sectors: Optional[str] = "Technology,Healthcare,Clean Energy"
    target_return: Optional[float] = 12.0
    experience_level: Optional[str] = "intermediate"
    notes: Optional[str] = None


class InvestorProfileCreate(InvestorProfileBase):
    pass


class InvestorProfileUpdate(BaseModel):
    risk_tolerance: Optional[str] = None
    investment_horizon: Optional[str] = None
    preferred_sectors: Optional[str] = None
    target_return: Optional[float] = None
    experience_level: Optional[str] = None
    notes: Optional[str] = None


class InvestorProfileResponse(InvestorProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
