from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.research.comparison_engine import comparison_engine
from app.services.research.thesis_builder import thesis_builder
from app.services.research.timeline_diff import timeline_diff_engine
from app.services.research.screener import screener_engine
from app.services.research.decision_journal import decision_journal_service

router = APIRouter()


class CompareRequest(BaseModel):
    symbol_a: str = Field(..., min_length=1, max_length=15)
    symbol_b: str = Field(..., min_length=1, max_length=15)


class ThesisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=15)
    save_to_db: bool = Field(False)


class ScreenRequest(BaseModel):
    sector: Optional[str] = None
    max_pe: Optional[float] = None
    min_pe: Optional[float] = None
    max_debt_to_equity: Optional[float] = None
    min_change_percent: Optional[float] = None
    limit: int = Field(10, ge=1, le=50)


class DiffRequest(BaseModel):
    previous_analysis: Dict[str, Any]
    current_analysis: Dict[str, Any]


class JournalCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=15)
    thesis_title: str = Field(..., min_length=3, max_length=255)
    reason: str = Field(..., min_length=5)
    risk_assessment: Optional[str] = None
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    notes: Optional[str] = None


# 1. Company Comparison
@router.post("/compare")
async def compare_companies(
    req: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Side-by-side company comparison with explicit 'Unavailable' handling for missing metrics."""
    return await comparison_engine.compare(
        db=db,
        symbol_a=req.symbol_a,
        symbol_b=req.symbol_b,
    )


# 2. Investment Thesis Builder
@router.post("/thesis")
async def build_research_thesis(
    req: ThesisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Generates an evidence-weighted thesis with Bull, Bear, and Devil's Advocate challenges."""
    return await thesis_builder.build_thesis(
        db=db,
        user_id=current_user.id,
        symbol=req.symbol,
        save_to_db=req.save_to_db,
    )


# 3. Deterministic Stock Screener
@router.post("/screen")
def screen_securities(
    req: ScreenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Factual database screener providing explicit 'Why Included?' attribution."""
    return screener_engine.screen_securities(
        db=db,
        sector=req.sector,
        max_pe=req.max_pe,
        min_pe=req.min_pe,
        max_debt_to_equity=req.max_debt_to_equity,
        min_change_percent=req.min_change_percent,
        limit=req.limit,
    )


# 4. Research Timeline
@router.get("/timeline/{symbol}")
def get_research_timeline(
    symbol: str,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Unified chronological timeline of past analyses, SEC filings, events, and alerts."""
    return timeline_diff_engine.get_research_timeline(
        db=db,
        symbol=symbol,
        user_id=current_user.id,
        limit=limit,
    )


# 5. Analysis Diff ("What Changed?")
@router.post("/diff")
def compute_analysis_diff(
    req: DiffRequest,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Computes structured differences between previous and current research analyses."""
    return timeline_diff_engine.compute_analysis_diff(
        previous=req.previous_analysis,
        current=req.current_analysis,
    )


# 6. Decision Journal
@router.get("/decision-journal")
def list_decision_journal(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """List recorded investment research journal entries for authenticated user."""
    entries = decision_journal_service.list_entries(db=db, user_id=current_user.id, symbol=symbol)
    return [
        {
            "id": e.id,
            "symbol": e.symbol,
            "thesis_title": e.thesis_title,
            "reason": e.reason,
            "risk_assessment": e.risk_assessment,
            "confidence": e.confidence,
            "notes": e.notes,
            "status": e.status,
            "date": e.date.isoformat() if e.date else None,
            "last_reviewed_at": e.last_reviewed_at.isoformat() if e.last_reviewed_at else None,
            "review_notes": e.review_notes,
        }
        for e in entries
    ]


@router.post("/decision-journal")
def create_decision_journal_entry(
    req: JournalCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Record a new investment research hypothesis into the Decision Journal."""
    entry = decision_journal_service.create_entry(
        db=db,
        user_id=current_user.id,
        symbol=req.symbol,
        thesis_title=req.thesis_title,
        reason=req.reason,
        risk_assessment=req.risk_assessment,
        confidence=req.confidence,
        notes=req.notes,
    )
    return {
        "id": entry.id,
        "symbol": entry.symbol,
        "thesis_title": entry.thesis_title,
        "status": entry.status,
        "message": "Research decision journal entry recorded successfully.",
    }


@router.post("/decision-journal/{entry_id}/review")
async def review_decision_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Autonomous retrospective review comparing original thesis against current market evidence."""
    try:
        return await decision_journal_service.review_entry(
            db=db,
            user_id=current_user.id,
            entry_id=entry_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
