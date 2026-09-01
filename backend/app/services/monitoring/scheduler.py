import asyncio
from datetime import datetime, timezone
import time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.models.monitoring import MonitoringRun, Alert, MarketEvent
from app.schemas.monitoring import SimulateEventRequest
from app.schemas.intelligence import AnalysisRequest
from app.services.agents.orchestrator import orchestrator
from app.services.monitoring.anomaly_detector import anomaly_detector, DetectedAnomaly
from app.services.monitoring.event_detector import event_detector
from app.services.monitoring.alert_prioritizer import alert_prioritizer


class MonitoringScheduler:
    """
    Local autonomous surveillance coordinator.
    Scans active watchlist and portfolio assets, detects statistical anomalies,
    routes events through specialized multi-agent investigations, and prioritizes proactive alerts.
    """

    @staticmethod
    async def run_surveillance_cycle(
        db: Session,
        user_id: Optional[int] = None,
        run_type: str = "manual",
    ) -> MonitoringRun:
        start_time = time.time()
        events_count = 0
        alerts_count = 0
        error_msg = None

        try:
            # 1. Discover all active symbols to monitor
            portfolios_q = db.query(Portfolio)
            watchlists_q = db.query(Watchlist)
            if user_id:
                portfolios_q = portfolios_q.filter(Portfolio.user_id == user_id)
                watchlists_q = watchlists_q.filter(Watchlist.user_id == user_id)

            portfolios = portfolios_q.all()
            watchlists = watchlists_q.all()

            user_holdings_weights: Dict[int, Dict[str, float]] = {}
            user_watchlist_symbols: Dict[int, set] = {}
            monitored_symbols = set()

            for p in portfolios:
                uid = p.user_id
                if uid not in user_holdings_weights:
                    user_holdings_weights[uid] = {}
                tot_val = sum(h.quantity * h.buy_price for h in p.holdings) if p.holdings else 0.0
                for h in p.holdings:
                    sym = h.symbol.upper()
                    monitored_symbols.add(sym)
                    pos_val = h.quantity * h.buy_price
                    weight = (pos_val / tot_val * 100) if tot_val > 0 else 0.0
                    user_holdings_weights[uid][sym] = weight

            for w in watchlists:
                uid = w.user_id
                if uid not in user_watchlist_symbols:
                    user_watchlist_symbols[uid] = set()
                if w.symbols:
                    for s in w.symbols.split(","):
                        sym = s.strip().upper()
                        if sym:
                            user_watchlist_symbols[uid].add(sym)
                            monitored_symbols.add(sym)

            # Fallback default if empty
            if not monitored_symbols:
                monitored_symbols = {"NVDA", "AAPL", "MSFT"}

            # 2. Scan monitored symbols for statistical anomalies
            for sym in monitored_symbols:
                anomalies = await anomaly_detector.scan_symbol(db, sym)
                for anom in anomalies:
                    events_count += 1

                    # Trigger multi-agent investigation based on anomaly type (Event -> Agent Routing)
                    if anom.event_type == "PRICE_ANOMALY":
                        analysis_type = "technical"
                    elif anom.event_type == "REGULATORY_FILING":
                        analysis_type = "fundamental"
                    else:
                        analysis_type = "comprehensive"

                    # Execute targeted investigation
                    req = AnalysisRequest(
                        query=f"Investigate {anom.title}. Analyze supporting and opposing factors.",
                        symbol=sym,
                        analysis_type=analysis_type,
                    )
                    analysis_resp = await orchestrator.run_analysis(
                        db=db,
                        user_id=user_id or 1,
                        request=req,
                    )

                    # Persist event and create alerts for affected users
                    target_users = [user_id] if user_id else list(user_holdings_weights.keys() | user_watchlist_symbols.keys())
                    for uid in target_users:
                        weight = user_holdings_weights.get(uid, {}).get(sym, 0.0)
                        is_in_wl = sym in user_watchlist_symbols.get(uid, set())

                        # Classify and persist MarketEvent
                        event_record = event_detector.classify_and_persist(
                            db=db,
                            anomaly=anom,
                            user_portfolio_weight=weight,
                        )

                        # Prioritize and persist Alert
                        alert_prioritizer.prioritize_and_persist(
                            db=db,
                            user_id=uid,
                            event=event_record,
                            portfolio_weight=weight,
                            is_in_watchlist=is_in_wl,
                            synthesis_data=analysis_resp.model_dump(),
                        )
                        alerts_count += 1

        except Exception as e:
            error_msg = str(e)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        run_status = "completed" if not error_msg else "failed"

        run_record = MonitoringRun(
            run_type=run_type,
            status=run_status,
            events_detected=events_count,
            alerts_created=alerts_count,
            execution_time_ms=elapsed_ms,
            error_message=error_msg,
            created_at=datetime.now(timezone.utc),
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)
        return run_record

    @staticmethod
    async def simulate_demo_event(
        db: Session,
        user_id: int,
        req: SimulateEventRequest,
    ) -> Alert:
        """
        Controlled demo simulation for hackathon judges.
        Simulates an intra-session price displacement or volume anomaly, triggers
        multi-agent investigation, conflict checks, and produces an explainable proactive alert.
        """
        sym = req.symbol.upper()
        direction = "drop" if req.price_change_pct < 0 else "surge"
        title = req.title or f"[DEMO] {sym} experienced sudden {abs(req.price_change_pct):.1f}% price {direction}"
        desc = req.description or (
            f"SIMULATED TEST EVENT: Real-time telemetry simulated abnormal {req.price_change_pct:+.1f}% price displacement "
            f"with {req.volume_multiple:.1f}x volume surge on {sym} to demonstrate autonomous surveillance."
        )

        anom = DetectedAnomaly(
            event_type=req.event_type,
            symbol=sym,
            magnitude=req.price_change_pct,
            title=title,
            description=desc,
            evidence=[
                f"Simulated Price Change: {req.price_change_pct:+.1f}%",
                f"Simulated Volume Multiple: {req.volume_multiple:.1f}x baseline",
                "Source: MATS Demo Event Simulator [Judging Mode]",
            ],
            confidence=0.96,
        )

        # Event -> Agent routing
        analysis_req = AnalysisRequest(
            query=f"Perform autonomous investigation of simulated {req.price_change_pct:+.1f}% shift in {sym}.",
            symbol=sym,
            analysis_type="comprehensive",
        )
        analysis_resp = await orchestrator.run_analysis(
            db=db,
            user_id=user_id,
            request=analysis_req,
        )

        # Get user's portfolio weight
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        weight = 0.0
        for p in portfolios:
            tot = sum(h.quantity * h.buy_price for h in p.holdings) if p.holdings else 0.0
            for h in p.holdings:
                if h.symbol.upper() == sym and tot > 0:
                    weight = (h.quantity * h.buy_price / tot) * 100

        # Classify event
        event_record = event_detector.classify_and_persist(
            db=db,
            anomaly=anom,
            user_portfolio_weight=weight,
        )

        # Prioritize alert
        alert = alert_prioritizer.prioritize_and_persist(
            db=db,
            user_id=user_id,
            event=event_record,
            portfolio_weight=weight,
            is_in_watchlist=True,
            synthesis_data=analysis_resp.model_dump(),
        )
        return alert


monitoring_scheduler = MonitoringScheduler()
