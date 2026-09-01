from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.audit.audit_service import audit_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update current user profile."""
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.password is not None and user_in.password.strip():
        current_user.hashed_password = get_password_hash(user_in.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    audit_service.log_event(
        db=db,
        action="USER_PROFILE_UPDATE",
        user_id=current_user.id,
        resource_type="User",
        resource_id=str(current_user.id),
        status="SUCCESS",
    )
    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    User Data Deletion (Right to be Forgotten).
    Cascades to portfolios, holdings, watchlists, alerts, and analysis history.
    """
    user_id = current_user.id
    email = current_user.email

    audit_service.log_event(
        db=db,
        action="USER_DATA_DELETION",
        user_id=user_id,
        resource_type="User",
        resource_id=str(user_id),
        details={"email": email, "reason": "user_requested_deletion"},
        status="SUCCESS",
    )

    db.delete(current_user)
    db.commit()

    return {"message": "User personal data and associated assets deleted successfully."}
