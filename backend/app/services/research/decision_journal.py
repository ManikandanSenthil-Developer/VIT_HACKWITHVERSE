from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.copilot import DecisionJournalEntry
from app.services.market.service import market_service
from app.models.market import Company, FundamentalData


class DecisionJournalService:
    """
    Manages investor decision research logs and conducts autonomous
    retrospective reviews comparing original hypotheses against new evidence.
    """

    @staticmethod
    def create_entry(
        db: Session,
        user_id: int,
        symbol: str,
        thesis_title: str,
        reason: str,
        risk_assessment: Optional[str] = None,
        confidence: float = 0.8,
        notes: Optional[str] = None,
    ) -> DecisionJournalEntry:
        sym = symbol.upper().strip()
        entry = DecisionJournalEntry(
            user_id=user_id,
            symbol=sym,
            thesis_title=thesis_title,
            reason=reason,
            risk_assessment=risk_assessment,
            confidence=confidence,
            notes=notes,
            status="ACTIVE",
            date=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def list_entries(
        db: Session,
        user_id: int,
        symbol: Optional[str] = None,
    ) -> List[DecisionJournalEntry]:
        query = db.query(DecisionJournalEntry).filter(DecisionJournalEntry.user_id == user_id)
        if symbol:
            query = query.filter(DecisionJournalEntry.symbol == symbol.upper().strip())
        return query.order_by(DecisionJournalEntry.date.desc()).all()

    @staticmethod
    async def review_entry(
        db: Session,
        user_id: int,
        entry_id: int,
    ) -> Dict[str, Any]:
        entry = (
            db.query(DecisionJournalEntry)
            .filter(DecisionJournalEntry.id == entry_id, DecisionJournalEntry.user_id == user_id)
            .first()
        )
        if not entry:
            raise ValueError(f"Decision journal entry {entry_id} not found or access denied.")

        sym = entry.symbol
        # Current quote
        try:
            q_resp = await market_service.get_quote(db, sym)
            curr_price = q_resp.data.price
            curr_chg = q_resp.data.change_percent
        except Exception:
            curr_price = 0.0
            curr_chg = 0.0

        # Fundamentals
        comp = db.query(Company).filter(Company.symbol == sym).first()
        fund = (
            db.query(FundamentalData)
            .filter(FundamentalData.symbol == sym)
            .order_by(FundamentalData.fiscal_year.desc())
            .first()
        )

        # Retrospective alignment check
        if curr_chg > 2.0:
            status = "SUPPORTED"
            review_notes = (
                f"Retrospective review: Price trajectory aligns positively ({curr_chg:+.2f}%). "
                f"Original hypothesis ('{entry.thesis_title}') remains consistent with ongoing trading patterns."
            )
        elif curr_chg < -4.0:
            status = "CONTRADICTED"
            review_notes = (
                f"Retrospective review: Price experienced sharp retracement ({curr_chg:+.2f}%). "
                f"Thesis assumption ('{entry.reason[:80]}...') is challenged by negative momentum."
            )
        else:
            status = "PARTIALLY_SUPPORTED"
            review_notes = (
                f"Retrospective review: Price movement is relatively neutral ({curr_chg:+.2f}%). "
                f"Ongoing surveillance recommended to confirm operational execution."
            )

        entry.status = status
        entry.last_reviewed_at = datetime.now(timezone.utc)
        entry.review_notes = review_notes
        db.commit()
        db.refresh(entry)

        return {
            "entry_id": entry.id,
            "symbol": entry.symbol,
            "thesis_title": entry.thesis_title,
            "status": entry.status,
            "last_reviewed_at": entry.last_reviewed_at.isoformat(),
            "review_notes": entry.review_notes,
            "current_price": curr_price,
            "current_change_percent": curr_chg,
        }


decision_journal_service = DecisionJournalService()
