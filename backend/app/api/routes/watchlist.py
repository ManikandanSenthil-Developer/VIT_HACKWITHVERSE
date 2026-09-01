from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse, WatchlistUpdate

router = APIRouter()


@router.get("/", response_model=List[WatchlistResponse])
def get_user_watchlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieve all watchlists for current user."""
    return db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    watchlist_in: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new watchlist."""
    watchlist = Watchlist(
        user_id=current_user.id,
        name=watchlist_in.name,
        description=watchlist_in.description,
        symbols=watchlist_in.symbols or "",
    )
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return watchlist


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist_by_id(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get single watchlist by ID."""
    watchlist = (
        db.query(Watchlist)
        .filter(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .first()
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return watchlist


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist(
    watchlist_id: int,
    watchlist_in: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a watchlist."""
    watchlist = (
        db.query(Watchlist)
        .filter(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .first()
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    update_data = watchlist_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(watchlist, field, value)

    db.commit()
    db.refresh(watchlist)
    return watchlist


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a watchlist."""
    watchlist = (
        db.query(Watchlist)
        .filter(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .first()
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    db.delete(watchlist)
    db.commit()
