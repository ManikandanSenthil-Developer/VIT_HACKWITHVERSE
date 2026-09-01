from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.schemas.investor_profile import InvestorProfileResponse, InvestorProfileUpdate

router = APIRouter()


@router.get("/", response_model=InvestorProfileResponse)
def read_investor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user's investor profile."""
    profile = db.query(InvestorProfile).filter(InvestorProfile.user_id == current_user.id).first()
    if not profile:
        # Create default profile if not present
        profile = InvestorProfile(
            user_id=current_user.id,
            risk_tolerance="moderate",
            investment_horizon="medium",
            preferred_sectors="Technology,Healthcare,Clean Energy",
            target_return=12.0,
            experience_level="intermediate",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/", response_model=InvestorProfileResponse)
def update_investor_profile(
    profile_in: InvestorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update current user's investor profile."""
    profile = db.query(InvestorProfile).filter(InvestorProfile.user_id == current_user.id).first()
    if not profile:
        profile = InvestorProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
