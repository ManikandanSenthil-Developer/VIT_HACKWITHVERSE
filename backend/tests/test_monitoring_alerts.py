import pytest
from app.services.monitoring.anomaly_detector import DetectedAnomaly
from app.services.monitoring.event_detector import event_detector
from app.services.monitoring.alert_prioritizer import alert_prioritizer
from app.models.monitoring import Alert, MarketEvent


def test_event_detector_severity_personalization(db_session):
    anomaly = DetectedAnomaly(
        event_type="PRICE_ANOMALY",
        symbol="TCS",
        magnitude=-4.2,
        title="TCS price dropped 4.2%",
        description="Significant drop observed.",
        evidence=["Price: $3400.00", "Change: -4.2%"],
        confidence=0.90,
    )

    # When user owns 0% of TCS -> Base severity is MEDIUM
    event_unowned = event_detector.classify_and_persist(db_session, anomaly, user_portfolio_weight=0.0)
    assert event_unowned.severity in ("MEDIUM", "LOW")

    # When user owns 35% of portfolio in TCS -> Upgraded to CRITICAL/HIGH
    anomaly2 = DetectedAnomaly(
        event_type="PRICE_ANOMALY",
        symbol="RELIANCE",
        magnitude=-5.0,
        title="RELIANCE price dropped 5.0%",
        description="Severe intraday drop.",
        evidence=["Price: $2800.00"],
        confidence=0.95,
    )
    event_heavy = event_detector.classify_and_persist(db_session, anomaly2, user_portfolio_weight=35.0)
    assert event_heavy.severity in ("HIGH", "CRITICAL")


def test_alert_prioritizer_and_deduplication(db_session):
    event = MarketEvent(
        symbol="NVDA",
        event_type="PRICE_ANOMALY",
        severity="HIGH",
        title="NVDA extreme price fluctuation",
        description="Abnormal deviation.",
        source="surveillance",
        confidence=0.88,
    )
    db_session.add(event)
    db_session.commit()

    # 1. Initial alert for user 1 (owns 25% of NVDA -> URGENT priority)
    alert1 = alert_prioritizer.prioritize_and_persist(
        db=db_session,
        user_id=1,
        event=event,
        portfolio_weight=25.0,
        is_in_watchlist=True,
    )
    assert alert1.priority == "URGENT"
    assert alert1.status == "NEW"

    # 2. Second event triggers deduplication (should cluster into existing alert, not duplicate)
    alert2 = alert_prioritizer.prioritize_and_persist(
        db=db_session,
        user_id=1,
        event=event,
        portfolio_weight=25.0,
        is_in_watchlist=True,
    )
    assert alert2.id == alert1.id
    assert "multiple" in alert2.title.lower() or "signals" in alert2.title.lower()


def test_monitoring_alerts_and_daily_brief_api_flow(client):
    # Register & Login User A
    client.post("/api/v1/auth/register", json={
        "email": "alert_user_a@mats.ai",
        "password": "SecurePassword123!",
        "full_name": "Alert User Alpha"
    })
    login_a = client.post("/api/v1/auth/login", json={
        "email": "alert_user_a@mats.ai",
        "password": "SecurePassword123!"
    })
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register & Login User B (for user isolation test)
    client.post("/api/v1/auth/register", json={
        "email": "alert_user_b@mats.ai",
        "password": "SecurePassword123!",
        "full_name": "Alert User Beta"
    })
    login_b = client.post("/api/v1/auth/login", json={
        "email": "alert_user_b@mats.ai",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Test POST /api/v1/monitoring/simulate-event for User A
    sim_res = client.post("/api/v1/monitoring/simulate-event", json={
        "symbol": "NVDA",
        "event_type": "PRICE_ANOMALY",
        "price_change_pct": -4.8,
        "volume_multiple": 2.3,
        "title": "NVDA Simulated Sudden Pullback",
    }, headers=headers_a)
    assert sim_res.status_code == 200
    alert_data = sim_res.json()
    assert alert_data["symbol"] == "NVDA"
    assert alert_data["status"] == "NEW"
    alert_id = alert_data["id"]

    # 2. Test GET /api/v1/alerts/ for User A
    alerts_res = client.get("/api/v1/alerts/", headers=headers_a)
    assert alerts_res.status_code == 200
    alerts_list = alerts_res.json()
    assert len(alerts_list) >= 1
    assert alerts_list[0]["id"] == alert_id

    # 3. User Isolation Test: User B should NOT see User A's alerts
    alerts_b_res = client.get("/api/v1/alerts/", headers=headers_b)
    assert alerts_b_res.status_code == 200
    assert len(alerts_b_res.json()) == 0

    # User B cannot update User A's alert
    patch_b = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "SEEN"}, headers=headers_b)
    assert patch_b.status_code == 404

    # 4. User A updates alert status: SEEN and ACKNOWLEDGED
    patch_a = client.patch(f"/api/v1/alerts/{alert_id}", json={
        "status": "SEEN",
        "feedback": "HELPFUL"
    }, headers=headers_a)
    assert patch_a.status_code == 200
    assert patch_a.json()["status"] == "SEEN"
    assert patch_a.json()["feedback"] == "HELPFUL"

    # 5. Test GET /api/v1/intelligence/feed
    feed_res = client.get("/api/v1/intelligence/feed", headers=headers_a)
    assert feed_res.status_code == 200
    assert len(feed_res.json()) >= 1

    # 6. Test GET /api/v1/intelligence/daily-brief
    brief_res = client.get("/api/v1/intelligence/daily-brief", headers=headers_a)
    assert brief_res.status_code == 200
    brief_data = brief_res.json()
    assert "portfolio_summary" in brief_data
    assert "key_developments" in brief_data
    assert len(brief_data["what_deserves_attention"]) > 0

    # 7. Test POST /api/v1/alerts/dismiss-all
    dismiss_res = client.post("/api/v1/alerts/dismiss-all", headers=headers_a)
    assert dismiss_res.status_code == 200

    # Verify alerts list is now empty of active alerts
    alerts_after_dismiss = client.get("/api/v1/alerts/", headers=headers_a)
    assert len(alerts_after_dismiss.json()) == 0
