import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.models.intelligence import AnalysisHistory
from app.models.monitoring import Alert
from app.models.copilot import DecisionJournalEntry
from app.models.audit import AuditLog
from app.models.ecosystem import UserAccessibilityPreference, UserFeedback
from app.services.providers.provider_interfaces import provider_health_monitor
from app.services.integrations.mock_broker import mock_broker_adapter
from app.services.provenance.provenance import provenance_service

router = APIRouter()


class AccessibilityPreferenceUpdate(BaseModel):
    language: Optional[str] = Field(None, description="Preferred language: 'en', 'ta', 'hi'")
    text_size: Optional[str] = Field(None, description="Text size: 'normal', 'large', 'extra_large'")
    reduced_motion: Optional[bool] = Field(None, description="Reduce animations for accessibility")
    high_contrast: Optional[bool] = Field(None, description="Enable high contrast mode")
    voice_enabled: Optional[bool] = Field(None, description="Enable voice-first audio interaction")


class UserFeedbackRequest(BaseModel):
    target_type: str = Field(..., description="Target category: COPILOT_MESSAGE, ALERT, ANALYSIS, THESIS")
    target_id: str = Field(..., description="Identifier of the target artifact or message")
    is_helpful: bool = Field(..., description="True if helpful, False if not helpful")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional user commentary")


class BrokerSyncRequest(BaseModel):
    account_id: Optional[str] = Field("ACC-DEMO-9942", description="Simulated brokerage account ID")


class SourceConflictCheckRequest(BaseModel):
    symbol: str
    metric: str
    source_a_name: str
    source_a_value: float
    source_a_hierarchy: str = "PRIMARY"
    source_b_name: str
    source_b_value: float
    source_b_hierarchy: str = "SECONDARY"


# 1. Accessibility Preferences
@router.get("/accessibility")
def get_accessibility_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    pref = db.query(UserAccessibilityPreference).filter(UserAccessibilityPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserAccessibilityPreference(
            user_id=current_user.id,
            language="en",
            text_size="normal",
            reduced_motion=False,
            high_contrast=False,
            voice_enabled=True,
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return {
        "user_id": current_user.id,
        "language": pref.language,
        "text_size": pref.text_size,
        "reduced_motion": pref.reduced_motion,
        "high_contrast": pref.high_contrast,
        "voice_enabled": pref.voice_enabled,
        "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
    }


@router.put("/accessibility")
def update_accessibility_preferences(
    req: AccessibilityPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    pref = db.query(UserAccessibilityPreference).filter(UserAccessibilityPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserAccessibilityPreference(user_id=current_user.id)
        db.add(pref)

    if req.language is not None:
        if req.language in ("en", "ta", "hi"):
            pref.language = req.language
    if req.text_size is not None:
        if req.text_size in ("normal", "large", "extra_large"):
            pref.text_size = req.text_size
    if req.reduced_motion is not None:
        pref.reduced_motion = req.reduced_motion
    if req.high_contrast is not None:
        pref.high_contrast = req.high_contrast
    if req.voice_enabled is not None:
        pref.voice_enabled = req.voice_enabled

    pref.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pref)

    return {
        "status": "SUCCESS",
        "message": "Accessibility preferences updated successfully.",
        "preferences": {
            "language": pref.language,
            "text_size": pref.text_size,
            "reduced_motion": pref.reduced_motion,
            "high_contrast": pref.high_contrast,
            "voice_enabled": pref.voice_enabled,
        },
    }


# 2. User Feedback Collection & Analytics
@router.post("/feedback")
def submit_user_feedback(
    req: UserFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    fb = UserFeedback(
        user_id=current_user.id,
        target_type=req.target_type.upper(),
        target_id=req.target_id,
        is_helpful=req.is_helpful,
        comment=req.comment,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return {
        "status": "SUCCESS",
        "feedback_id": fb.id,
        "message": "Feedback recorded successfully for product quality monitoring.",
    }


@router.get("/feedback/analytics")
def get_feedback_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    feedbacks = db.query(UserFeedback).all()
    total = len(feedbacks)
    helpful_count = sum(1 for f in feedbacks if f.is_helpful)
    not_helpful_count = total - helpful_count
    helpful_pct = round((helpful_count / total * 100.0), 1) if total > 0 else 100.0

    return {
        "total_feedbacks": total,
        "helpful_count": helpful_count,
        "not_helpful_count": not_helpful_count,
        "helpful_percentage": helpful_pct,
        "categories": {
            "copilot": sum(1 for f in feedbacks if "COPILOT" in f.target_type),
            "alerts": sum(1 for f in feedbacks if "ALERT" in f.target_type),
            "analyses": sum(1 for f in feedbacks if "ANALYSIS" in f.target_type),
        },
    }


# 3. Social Impact & Telemetry Metrics
@router.get("/impact")
def get_social_impact_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    user_count = db.query(User).count()
    analyses_count = db.query(AnalysisHistory).count()
    alerts_count = db.query(Alert).count()

    # Honest estimation clearly labeled as ESTIMATE
    estimated_hours = round(((analyses_count * 45.0) + (alerts_count * 15.0)) / 60.0, 1)

    return {
        "users_onboarded": user_count,
        "analyses_completed": analyses_count,
        "alerts_generated": alerts_count,
        "estimated_research_time_saved_hours": estimated_hours,
        "time_savings_metric_type": "ESTIMATE",
        "languages_supported_count": 3,
        "supported_languages": ["English", "தமிழ் (Tamil)", "हिन्दी (Hindi)"],
        "voice_interactions_enabled": True,
        "accessible_modes_available": [
            "Normal Text",
            "Large Text (+2px)",
            "Extra Large Text (+4px)",
            "High Contrast (WCAG AAA)",
            "Reduced Motion",
        ],
        "decision_support_boundary": "100% Non-custodial research intelligence",
    }


# 4. User Data Portability (JSON & CSV Export)
@router.get("/export")
def export_user_data(
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Exports the authenticated user's data for portability and GDPR compliance.
    Strictly isolated to current_user.id; zero cross-tenant data leakage.
    """
    user_data = {
        "user_profile": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "portfolios": [
            {
                "id": p.id,
                "name": p.name,
                "cash_balance": p.cash_balance,
                "holdings": [
                    {
                        "symbol": h.symbol,
                        "quantity": h.quantity,
                        "buy_price": h.buy_price,
                        "current_value": h.current_value,
                    }
                    for h in p.holdings
                ],
            }
            for p in current_user.portfolios
        ],
        "watchlists": [
            {"id": w.id, "name": w.name, "symbols": [item.symbol for item in w.items]}
            for w in current_user.watchlists
        ],
        "decision_journal": [
            {
                "id": j.id,
                "symbol": j.symbol,
                "thesis_title": j.thesis_title,
                "reason": j.reason,
                "status": j.status,
                "confidence": j.confidence,
                "date": j.date.isoformat() if j.date else None,
            }
            for j in db.query(DecisionJournalEntry).filter(DecisionJournalEntry.user_id == current_user.id).all()
        ],
        "alerts_history": [
            {"id": a.id, "symbol": a.symbol, "title": a.title, "priority": a.priority, "status": a.status}
            for a in current_user.alerts
        ],
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Category", "Entity ID", "Symbol / Name", "Detail A", "Detail B", "Status / Value"])

        for p in user_data["portfolios"]:
            writer.writerow(["Portfolio", p["id"], p["name"], f"Cash: ${p['cash_balance']}", f"{len(p['holdings'])} holdings", "Active"])
            for h in p["holdings"]:
                writer.writerow(["Holding", p["id"], h["symbol"], f"Qty: {h['quantity']}", f"Buy: ${h['buy_price']}", f"Val: ${h['current_value']}"])

        for j in user_data["decision_journal"]:
            writer.writerow(["DecisionJournal", j["id"], j["symbol"], j["thesis_title"], f"Confidence: {j['confidence']}", j["status"]])

        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=mats_user_export_{current_user.id}.csv"},
        )

    return user_data


# 5. External Provider Health Status
@router.get("/providers/health")
def get_providers_health() -> List[Dict[str, Any]]:
    """Returns telemetry and runtime status for external and internal data providers."""
    statuses = provider_health_monitor.get_all_statuses()
    return [s.model_dump() for s in statuses]


# 6. Read-Only Mock Brokerage Sync
@router.post("/broker/sync")
def sync_mock_broker(
    req: BrokerSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Synchronizes portfolio holdings from mock broker (paper trading sandbox).
    Strictly read-only; trade placement is completely disabled.
    """
    return mock_broker_adapter.sync_broker_portfolio(
        db=db,
        user_id=current_user.id,
        account_id=req.account_id or "ACC-DEMO-9942",
    )


# 7. Financial Concept Education Cards
@router.get("/education/{concept}")
def get_financial_education(
    concept: str,
    language: Optional[str] = "en",
) -> Dict[str, Any]:
    """
    Returns structured, non-personalized educational explanations
    for complex financial indicators and metrics.
    """
    c_key = concept.lower().strip()
    glossary = {
        "pe_ratio": {
            "title": "Price-to-Earnings (P/E) Ratio",
            "simple_definition": "Measures how much investors are willing to pay for each dollar of a company's annual earnings.",
            "example": "A P/E of 25x means you pay $25 for every $1 of reported net income.",
            "why_it_matters": "Helps compare relative valuation between peer companies in the same sector.",
            "limitations": "Does not account for debt leverage, cash flow quality, or cyclical growth variations.",
        },
        "volatility": {
            "title": "Market Volatility & Price Dispersion",
            "simple_definition": "The statistical measure of how rapidly and dramatically an asset's price fluctuates over time.",
            "example": "An annualized volatility of 40% indicates large swings and higher uncertainty.",
            "why_it_matters": "Higher volatility implies larger potential drawdowns and wider dispersion of potential outcomes.",
            "limitations": "Volatility measures movement, not permanent capital loss or business quality.",
        },
        "drawdown": {
            "title": "Maximum Drawdown (Peak-to-Trough Decline)",
            "simple_definition": "The percentage decline from an investment's highest peak to its lowest subsequent trough before a new peak is achieved.",
            "example": "If a portfolio drops from $10,000 to $7,500, the maximum drawdown is 25%.",
            "why_it_matters": "Tests an investor's psychological resilience and ability to remain invested through market stress.",
            "limitations": "Measures historical pain; does not predict future drawdown duration.",
        },
        "diversification": {
            "title": "Portfolio Diversification & Correlation",
            "simple_definition": "Allocating capital across uncorrelated assets or sectors to reduce idiosyncratic risk.",
            "example": "Holding technology, healthcare, and cash rather than 100% in a single semiconductor stock.",
            "why_it_matters": "Ensures that a single adverse corporate shock does not impair your entire life savings.",
            "limitations": "Diversification cannot eliminate systemic macro market risk.",
        },
        "concentration": {
            "title": "Position Concentration Exposure",
            "simple_definition": "The proportion of total portfolio capital allocated to a single holding or sector.",
            "example": "If NVDA represents 45% of your portfolio, your portfolio is highly concentrated in semiconductors.",
            "why_it_matters": "Amplifies single-stock volatility and idiosyncratic corporate risk factors.",
            "limitations": "Concentration can drive outsized returns during bull markets but elevates downside vulnerability.",
        },
    }

    item = glossary.get(c_key, glossary["pe_ratio"])
    return {
        "concept": c_key,
        "language": language or "en",
        "title": item["title"],
        "simple_definition": item["simple_definition"],
        "example": item["example"],
        "why_it_matters": item["why_it_matters"],
        "limitations": item["limitations"],
        "disclaimer": "EDUCATIONAL EXPLANATION ONLY. Not personalized investment advice.",
    }


# 8. Source Conflict Detection Endpoint
@router.post("/source-conflict-check")
def check_source_conflict(req: SourceConflictCheckRequest) -> Dict[str, Any]:
    """Detects and reports divergences between independent market providers."""
    source_a = {
        "name": req.source_a_name,
        "value": req.source_a_value,
        "hierarchy": req.source_a_hierarchy,
    }
    source_b = {
        "name": req.source_b_name,
        "value": req.source_b_value,
        "hierarchy": req.source_b_hierarchy,
    }
    report = provenance_service.detect_source_conflict(
        symbol=req.symbol,
        metric=req.metric,
        source_a=source_a,
        source_b=source_b,
    )
    return report.model_dump()
