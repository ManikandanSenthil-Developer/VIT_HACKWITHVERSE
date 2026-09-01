import pytest
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.watchlist import Watchlist
from app.models.market import Company, Security, MarketSnapshot, FundamentalData
from app.models.document import Document, DocumentChunk
from app.services.embeddings.embedding_service import embedding_service
from datetime import datetime, timezone


@pytest.fixture
def demo_setup():
    """Ensure database has baseline demo records for tests."""
    db = TestingSessionLocal()
    try:
        # Create demo user if absent
        user = db.query(User).filter(User.email == "demo_tester@mats.ai").first()
        if not user:
            user = User(
                email="demo_tester@mats.ai",
                hashed_password=get_password_hash("Password123!"),
                full_name="Demo Test Investor",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Portfolio
        port = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        if not port:
            port = Portfolio(user_id=user.id, name="Test Portfolio", cash_balance=10000.0)
            db.add(port)
            db.commit()
            db.refresh(port)

        # Holding
        h = db.query(Holding).filter(Holding.portfolio_id == port.id, Holding.symbol == "NVDA").first()
        if not h:
            h = Holding(portfolio_id=port.id, symbol="NVDA", quantity=25.0, buy_price=120.0, current_value=3000.0)
            db.add(h)
            db.commit()

        # Company & Snapshot
        comp = db.query(Company).filter(Company.symbol == "NVDA").first()
        if not comp:
            comp = Company(symbol="NVDA", name="NVIDIA Corporation", sector="Technology", industry="Semiconductors")
            db.add(comp)
            db.commit()
            db.refresh(comp)

        sec = db.query(Security).filter(Security.symbol == "NVDA").first()
        if not sec:
            sec = Security(company_id=comp.id, symbol="NVDA", name="NVIDIA Corp", security_type="Common Stock")
            db.add(sec)
            db.commit()
            db.refresh(sec)

        snap = db.query(MarketSnapshot).filter(MarketSnapshot.symbol == "NVDA").first()
        if not snap:
            snap = MarketSnapshot(
                security_id=sec.id,
                symbol="NVDA",
                price=128.50,
                change=2.5,
                change_percent=2.0,
                timestamp=datetime.now(timezone.utc),
                is_fresh=True,
            )
            db.add(snap)
            db.commit()

        return user.id
    finally:
        db.close()


def test_demo_status_endpoint(client: TestClient, demo_setup):
    """Verify GET /api/v1/demo/status reports status and subsystem counts."""
    res = client.get("/api/v1/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "companies_count" in data
    assert "documents_count" in data


def test_monitoring_metrics_endpoint(client: TestClient):
    """Verify GET /api/v1/monitoring/metrics returns operational telemetry."""
    res = client.get("/api/v1/monitoring/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "performance" in data
    assert "telemetry" in data
    assert data["performance"]["agent_success_rate_pct"] >= 95.0
    assert "active_agents" in data["cluster"]


def test_demo_scenario_1_execution(client: TestClient, demo_setup):
    """Verify Scenario 1 runs multi-agent analysis with citations on NVDA."""
    # Login as demo tester
    login = client.post("/api/v1/auth/login", json={"email": "demo_tester@mats.ai", "password": "Password123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/demo/scenarios/1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "NVDA"
    assert len(data["agents"]) >= 2
    assert "confidence" in data
    assert "recommendation" in data


def test_demo_scenario_3_portfolio_alert(client: TestClient, demo_setup):
    """Verify Scenario 3 detects portfolio movement, upgrades severity, and issues alert."""
    login = client.post("/api/v1/auth/login", json={"email": "demo_tester@mats.ai", "password": "Password123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/demo/scenarios/3", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "NVDA"
    assert data["event_detected"]["type"] in ["PRICE_ANOMALY", "PRICE_PLUNGE", "PRICE_SURGE"]
    assert data["alert_created"]["severity"] in ["HIGH", "CRITICAL", "URGENT"]
    assert "updated_portfolio_risk_score" in data


def test_demo_reset_endpoint(client: TestClient, demo_setup):
    """Verify POST /api/v1/demo/reset restores baseline holdings and returns success."""
    login = client.post("/api/v1/auth/login", json={"email": "demo_tester@mats.ai", "password": "Password123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/demo/reset", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "4 holdings re-seeded" in data["message"]
