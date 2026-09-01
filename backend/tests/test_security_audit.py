import pytest
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash
from app.core.rate_limiter import rate_limiter
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.monitoring import Alert
from app.models.audit import AuditLog


@pytest.fixture(autouse=True)
def clean_rate_limiter():
    rate_limiter.clear()
    yield
    rate_limiter.clear()


@pytest.fixture
def two_users():
    """Create User A and User B with portfolios and alerts."""
    db = TestingSessionLocal()
    try:
        # Clean existing test users if any
        db.query(User).filter(User.email.in_(["user_a@mats.ai", "user_b@mats.ai", "delete_me@mats.ai"])).delete(synchronize_session=False)
        db.commit()

        # User A
        user_a = User(
            email="user_a@mats.ai",
            hashed_password=get_password_hash("PasswordA123!"),
            full_name="User Alpha",
            is_active=True,
        )
        # User B
        user_b = User(
            email="user_b@mats.ai",
            hashed_password=get_password_hash("PasswordB123!"),
            full_name="User Beta",
            is_active=True,
        )
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        # Portfolios
        port_a = Portfolio(user_id=user_a.id, name="Alpha Portfolio", cash_balance=10000.0)
        port_b = Portfolio(user_id=user_b.id, name="Beta Portfolio", cash_balance=20000.0)
        db.add_all([port_a, port_b])
        db.commit()
        db.refresh(port_a)
        db.refresh(port_b)

        # Alerts
        alert_b = Alert(
            user_id=user_b.id,
            symbol="AAPL",
            priority="URGENT",
            severity="HIGH",
            title="Beta Alert",
            explanation="Confidential Beta Alert",
            status="NEW",
            feedback="UNSPECIFIED",
        )
        db.add(alert_b)
        db.commit()
        db.refresh(alert_b)

        port_a_id = port_a.id
        port_b_id = port_b.id
        alert_b_id = alert_b.id

        return port_a_id, port_b_id, alert_b_id
    finally:
        db.close()


def test_idor_portfolio_isolation(client: TestClient, two_users):
    """Test that User A cannot access or mutate User B's portfolio (IDOR defense)."""
    port_a_id, port_b_id, _ = two_users

    # Login as User A
    res_a = client.post("/api/v1/auth/login", json={"email": "user_a@mats.ai", "password": "PasswordA123!"})
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A attempts to view User B's portfolio
    res_idor = client.get(f"/api/v1/portfolio/{port_b_id}", headers=headers_a)
    assert res_idor.status_code == 404, "User A must not be able to read User B's portfolio"

    # User A attempts to delete User B's portfolio
    res_del = client.delete(f"/api/v1/portfolio/{port_b_id}", headers=headers_a)
    assert res_del.status_code == 404, "User A must not be able to delete User B's portfolio"

    # User A attempts to add a holding to User B's portfolio
    res_add = client.post(
        f"/api/v1/portfolio/{port_b_id}/holdings",
        headers=headers_a,
        json={"symbol": "NVDA", "quantity": 10.0, "buy_price": 100.0},
    )
    assert res_add.status_code == 404, "User A must not be able to add holdings to User B's portfolio"


def test_idor_alerts_isolation(client: TestClient, two_users):
    """Test that User A cannot view or dismiss User B's proactive intelligence alerts."""
    _, _, alert_b_id = two_users

    res_a = client.post("/api/v1/auth/login", json={"email": "user_a@mats.ai", "password": "PasswordA123!"})
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A queries their alerts - alert_b must not appear
    res_alerts = client.get("/api/v1/alerts/", headers=headers_a)
    assert res_alerts.status_code == 200
    alert_ids = [a["id"] for a in res_alerts.json()]
    assert alert_b_id not in alert_ids, "User B's alert must not leak into User A's alerts feed"

    # User A attempts to mutate User B's alert
    res_patch = client.patch(
        f"/api/v1/alerts/{alert_b_id}",
        headers=headers_a,
        json={"status": "DISMISSED"},
    )
    assert res_patch.status_code == 404, "User A must not be able to mutate User B's alert"


def test_rate_limiting_enforcement(client: TestClient):
    """Verify that rapid repeated requests exceed sliding window limits and return 429."""
    rate_limiter.clear()

    # Login rate limit is 15 requests/min. Rapidly execute 15 requests.
    for i in range(15):
        res = client.post("/api/v1/auth/login", json={"email": "invalid@test.com", "password": "WrongPassword!"})
        assert res.status_code in [401, 200]

    # 16th request must be rate limited
    res_limited = client.post("/api/v1/auth/login", json={"email": "invalid@test.com", "password": "WrongPassword!"})
    assert res_limited.status_code == 429
    assert "Retry-After" in res_limited.headers
    assert "Rate limit exceeded" in res_limited.json()["detail"]


def test_security_headers_and_correlation_id(client: TestClient):
    """Verify that every response attaches security headers and an X-Request-ID."""
    res = client.get("/health")
    assert res.status_code == 200

    # Defensive Security Headers
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in res.headers

    # Correlation ID
    request_id = res.headers.get("X-Request-ID")
    assert request_id is not None
    assert request_id.startswith("MATS-REQ-")


def test_health_telemetry_probes(client: TestClient):
    """Verify detailed /health, /health/live, and /health/ready endpoints."""
    # Full health
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "components" in data
    assert data["components"]["database"] == "healthy"
    assert data["components"]["ai_agents"]["technical_agent"] == "online"

    # Liveness probe
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    # Readiness probe
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"


def test_user_data_deletion_cascades(client: TestClient):
    """Test GDPR-style user data deletion ('Right to be Forgotten') and clean cascading."""
    db = TestingSessionLocal()
    try:
        # Create user with holdings and alert
        user = User(
            email="delete_me@mats.ai",
            hashed_password=get_password_hash("Password123!"),
            full_name="To Be Deleted",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        port = Portfolio(user_id=user.id, name="Disposable Portfolio", cash_balance=5000.0)
        db.add(port)
        db.commit()
        db.refresh(port)

        holding = Holding(portfolio_id=port.id, symbol="MSFT", quantity=5.0, buy_price=300.0)
        alert = Alert(user_id=user.id, symbol="MSFT", priority="FYI", severity="LOW", title="Test", explanation="Test")
        db.add_all([holding, alert])
        db.commit()
        user_id = user.id
        port_id = port.id
        holding_id = holding.id
    finally:
        db.close()

    # Login
    res_login = client.post("/api/v1/auth/login", json={"email": "delete_me@mats.ai", "password": "Password123!"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete account
    res_del = client.delete("/api/v1/user/me", headers=headers)
    assert res_del.status_code == 200
    assert "deleted successfully" in res_del.json()["message"]

    # Verify user is gone
    check_db = TestingSessionLocal()
    try:
        user_check = check_db.query(User).filter(User.id == user_id).first()
        assert user_check is None

        # Verify portfolio and holding cascaded cleanly
        port_check = check_db.query(Portfolio).filter(Portfolio.id == port_id).first()
        assert port_check is None
        holding_check = check_db.query(Holding).filter(Holding.id == holding_id).first()
        assert holding_check is None

        # Verify audit log recorded deletion event
        audit_entry = check_db.query(AuditLog).filter(AuditLog.action == "USER_DATA_DELETION").first()
        assert audit_entry is not None
        assert "delete_me@mats.ai" in audit_entry.details_json
    finally:
        check_db.close()
