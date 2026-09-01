from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.schemas.risk import ScenarioRequest, ScenarioResponse, ScenarioHoldingImpact
from app.services.market.service import market_service
from app.services.risk.portfolio_intelligence import SECTOR_MAP


class ScenarioEngine:
    """
    Deterministic What-If mathematical scenario simulation engine.
    Calculates exact dollar and percentage portfolio impacts of hypothetical market shocks.
    Strictly marked as non-predictive mathematical calculations.
    """

    @staticmethod
    async def run_scenario(
        db: Session,
        portfolio: Portfolio,
        request: ScenarioRequest,
    ) -> ScenarioResponse:
        holdings: List[Holding] = portfolio.holdings or []
        target_sym = request.target_symbol.upper() if request.target_symbol else None
        target_sec = request.target_sector.lower() if request.target_sector else None
        pct_change = request.percentage_change
        factor = 1.0 + (pct_change / 100.0)

        current_holdings_total = 0.0
        scenario_holdings_total = 0.0
        impacts: List[ScenarioHoldingImpact] = []

        for h in holdings:
            sym = h.symbol.upper()
            try:
                quote_resp = await market_service.get_quote(db, sym)
                curr_price = quote_resp.data.price
            except Exception:
                curr_price = h.buy_price

            curr_val = round(h.quantity * curr_price, 2)
            current_holdings_total += curr_val

            # Determine whether this holding is subject to the shock
            h_sector = SECTOR_MAP.get(sym, "Diversified Equities").lower()
            is_affected = False

            if request.shock_type == "holding_shock":
                if target_sym and sym == target_sym:
                    is_affected = True
            elif request.shock_type == "sector_shock":
                if target_sec and (target_sec in h_sector or h_sector in target_sec):
                    is_affected = True
            elif request.shock_type == "position_rebalance":
                if target_sym and sym == target_sym:
                    is_affected = True

            if is_affected:
                if request.shock_type == "position_rebalance" and request.quantity_adjustment is not None:
                    new_qty = max(0.0, h.quantity + request.quantity_adjustment)
                    scen_price = curr_price
                    scen_val = round(new_qty * scen_price, 2)
                else:
                    scen_price = round(curr_price * factor, 2)
                    scen_val = round(h.quantity * scen_price, 2)

                val_diff = round(scen_val - curr_val, 2)
                diff_pct = round((val_diff / curr_val * 100), 2) if curr_val > 0 else 0.0
            else:
                scen_price = curr_price
                scen_val = curr_val
                val_diff = 0.0
                diff_pct = 0.0

            scenario_holdings_total += scen_val

            impacts.append(
                ScenarioHoldingImpact(
                    symbol=sym,
                    current_price=curr_price,
                    scenario_price=scen_price,
                    current_value=curr_val,
                    scenario_value=scen_val,
                    value_difference=val_diff,
                    difference_percent=diff_pct,
                )
            )

        current_total = round(portfolio.cash_balance + current_holdings_total, 2)
        scenario_total = round(portfolio.cash_balance + scenario_holdings_total, 2)
        total_diff_usd = round(scenario_total - current_total, 2)
        total_diff_pct = round((total_diff_usd / current_total * 100), 2) if current_total > 0 else 0.0

        target_desc = target_sym if target_sym else (target_sec or "Broad Portfolio")
        scenario_name = f"{target_desc} {pct_change:+.1f}% Stress Test"

        return ScenarioResponse(
            portfolio_id=portfolio.id,
            scenario_name=scenario_name,
            shock_type=request.shock_type,
            target=target_desc,
            percentage_change=pct_change,
            current_total_value=current_total,
            scenario_total_value=scenario_total,
            total_difference_usd=total_diff_usd,
            total_difference_percent=total_diff_pct,
            holdings_impact=impacts,
        )


scenario_engine = ScenarioEngine()
