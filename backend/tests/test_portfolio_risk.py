import pytest
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.schemas.risk import PositionHealth, SectorExposure, ScenarioRequest
from app.services.risk.risk_engine import risk_engine
from app.services.risk.scenario_engine import scenario_engine


def test_deterministic_risk_score_and_explainability():
    # Test 1: Concentrated portfolio with 1 large holding (> 50%)
    positions_conc = [
        PositionHealth(
            symbol="NVDA",
            quantity=100.0,
            buy_price=100.0,
            current_price=120.0,
            current_value=12000.0,
            unrealized_pnl=2000.0,
            pnl_percent=20.0,
            weight_percent=60.0,
            sector="Semiconductors & AI Hardware",
        ),
        PositionHealth(
            symbol="AAPL",
            quantity=50.0,
            buy_price=150.0,
            current_price=160.0,
            current_value=8000.0,
            unrealized_pnl=500.0,
            pnl_percent=6.67,
            weight_percent=40.0,
            sector="Consumer Technology & Services",
        ),
    ]
    sectors_conc = [
        SectorExposure(sector="Semiconductors & AI Hardware", value=12000.0, weight_percent=60.0),
        SectorExposure(sector="Consumer Technology & Services", value=8000.0, weight_percent=40.0),
    ]
    metrics_conc = {"top_weight": 60.0, "hhi": 0.52}

    explanation_conc = risk_engine.evaluate_risk(
        positions=positions_conc,
        sector_exposures=sectors_conc,
        metrics=metrics_conc,
        active_events_count=1,
        annualized_vol=42.0,
        max_drawdown=22.0,
    )

    assert explanation_conc.risk_level in ("HIGH", "CRITICAL")
    assert explanation_conc.risk_score >= 60
    assert len(explanation_conc.reasons) > 0
    assert any("concentration" in r.lower() for r in explanation_conc.reasons)

    # Verify mathematical explainability: sum of factor contributions equals total score
    factor_sum = sum(f.contribution for f in explanation_conc.factor_contributions)
    assert abs(factor_sum - explanation_conc.risk_score) <= 1.0


def test_diversified_portfolio_lower_risk():
    # Test 2: Diversified portfolio across 4 sectors with <= 25% max weight
    positions_div = [
        PositionHealth(symbol="NVDA", quantity=10, buy_price=100, current_price=100, current_value=1000, unrealized_pnl=0, pnl_percent=0, weight_percent=25, sector="Technology"),
        PositionHealth(symbol="JNJ", quantity=10, buy_price=100, current_price=100, current_value=1000, unrealized_pnl=0, pnl_percent=0, weight_percent=25, sector="Healthcare"),
        PositionHealth(symbol="XOM", quantity=10, buy_price=100, current_price=100, current_value=1000, unrealized_pnl=0, pnl_percent=0, weight_percent=25, sector="Energy"),
        PositionHealth(symbol="JPM", quantity=10, buy_price=100, current_price=100, current_value=1000, unrealized_pnl=0, pnl_percent=0, weight_percent=25, sector="Financials"),
    ]
    sectors_div = [
        SectorExposure(sector="Technology", value=1000, weight_percent=25),
        SectorExposure(sector="Healthcare", value=1000, weight_percent=25),
        SectorExposure(sector="Energy", value=1000, weight_percent=25),
        SectorExposure(sector="Financials", value=1000, weight_percent=25),
    ]
    metrics_div = {"top_weight": 25.0, "hhi": 0.25}

    explanation_div = risk_engine.evaluate_risk(
        positions=positions_div,
        sector_exposures=sectors_div,
        metrics=metrics_div,
        active_events_count=0,
        annualized_vol=18.0,
        max_drawdown=12.0,
    )

    assert explanation_div.risk_level in ("LOW", "MODERATE")
    assert explanation_div.risk_score < 50


@pytest.mark.anyio
async def test_scenario_mathematical_stress_testing(db_session):
    portfolio = Portfolio(
        user_id=1,
        name="Quant Testing Fund",
        total_value=10000.0,
        cash_balance=2000.0,
        currency="USD",
    )
    db_session.add(portfolio)
    db_session.commit()

    holding1 = Holding(
        portfolio_id=portfolio.id,
        symbol="NVDA",
        quantity=50.0,
        buy_price=100.0,
        current_value=5000.0,
    )
    holding2 = Holding(
        portfolio_id=portfolio.id,
        symbol="AAPL",
        quantity=20.0,
        buy_price=150.0,
        current_value=3000.0,
    )
    db_session.add_all([holding1, holding2])
    db_session.commit()
    db_session.refresh(portfolio)

    # Run scenario: NVDA falls 10%
    req = ScenarioRequest(
        portfolio_id=portfolio.id,
        shock_type="holding_shock",
        target_symbol="NVDA",
        percentage_change=-10.0,
    )

    scenario_res = await scenario_engine.run_scenario(db_session, portfolio, req)

    assert scenario_res.shock_type == "holding_shock"
    assert scenario_res.target == "NVDA"
    assert scenario_res.percentage_change == -10.0
    # NVDA position should drop by 10% of its valuation
    nvda_impact = next(h for h in scenario_res.holdings_impact if h.symbol == "NVDA")
    assert nvda_impact.value_difference < 0
    assert abs(nvda_impact.difference_percent - (-10.0)) < 0.1

    # AAPL should be unaffected
    aapl_impact = next(h for h in scenario_res.holdings_impact if h.symbol == "AAPL")
    assert aapl_impact.value_difference == 0.0
    assert aapl_impact.difference_percent == 0.0

    # Total difference should match NVDA value difference
    assert abs(scenario_res.total_difference_usd - nvda_impact.value_difference) < 0.01


def test_portfolio_health_and_scenarios_api_flow(client):
    # Register & Login
    client.post("/api/v1/auth/register", json={
        "email": "risk_investor@mats.ai",
        "password": "SecurePassword123!",
        "full_name": "Risk Quant Specialist"
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "risk_investor@mats.ai",
        "password": "SecurePassword123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create portfolio
    port_res = client.post("/api/v1/portfolio/", json={
        "name": "Institutional Tech Fund",
        "cash_balance": 15000.0,
    }, headers=headers)
    assert port_res.status_code == 201
    port_id = port_res.json()["id"]

    # Add holdings
    client.post(f"/api/v1/portfolio/{port_id}/holdings", json={
        "symbol": "NVDA",
        "quantity": 50.0,
        "buy_price": 110.0,
        "asset_type": "Stock",
    }, headers=headers)
    client.post(f"/api/v1/portfolio/{port_id}/holdings", json={
        "symbol": "MSFT",
        "quantity": 30.0,
        "buy_price": 380.0,
        "asset_type": "Stock",
    }, headers=headers)

    # 1. Test GET /api/v1/risk/portfolio/{id}
    health_res = client.get(f"/api/v1/risk/portfolio/{port_id}", headers=headers)
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["portfolio_id"] == port_id
    assert health_data["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert "risk_explanation" in health_data
    assert len(health_data["positions"]) == 2
    assert len(health_data["sector_breakdown"]) > 0

    # 2. Test POST /api/v1/scenarios/run
    scen_payload = {
        "portfolio_id": port_id,
        "shock_type": "holding_shock",
        "target_symbol": "NVDA",
        "percentage_change": -10.0,
    }
    scen_res = client.post("/api/v1/scenarios/run", json=scen_payload, headers=headers)
    assert scen_res.status_code == 200
    scen_data = scen_res.json()
    assert scen_data["target"] == "NVDA"
    assert scen_data["percentage_change"] == -10.0
    assert scen_data["total_difference_usd"] < 0
    assert len(scen_data["holdings_impact"]) == 2
