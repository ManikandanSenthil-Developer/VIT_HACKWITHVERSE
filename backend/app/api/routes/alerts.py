from datetime import datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.monitoring import Alert
from app.models.user import User
from app.schemas.monitoring import AlertItem, AlertUpdate

router = APIRouter()


@router.get("/", response_model=List[AlertItem])
def get_user_alerts(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority_filter: Optional[str] = Query(default=None, alias="priority"),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve prioritized proactive intelligence alerts for authenticated user."""
    q = db.query(Alert).filter(Alert.user_id == current_user.id)

    if status_filter:
        q = q.filter(Alert.status == status_filter.upper())
    else:
        # Default: hide dismissed
        q = q.filter(Alert.status != "DISMISSED")

    if priority_filter:
        q = q.filter(Alert.priority == priority_filter.upper())

    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@router.patch("/{alert_id}", response_model=AlertItem)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update alert lifecycle status (SEEN, ACKNOWLEDGED, DISMISSED) and user feedback."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found or access denied.",
        )

    if payload.status:
        st = payload.status.upper()
        alert.status = st
        if st == "SEEN" and not alert.seen_at:
            alert.seen_at = datetime.now(timezone.utc)

    if payload.feedback:
        alert.feedback = payload.feedback.upper()

    db.commit()
    db.refresh(alert)
    return alert


@router.post("/dismiss-all")
def dismiss_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Dismiss all active alerts for current user."""
    db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.status.in_(["NEW", "SEEN", "ACKNOWLEDGED"]),
    ).update({"status": "DISMISSED"}, synchronize_session=False)
    db.commit()
    return {"message": "All active alerts dismissed successfully."}
