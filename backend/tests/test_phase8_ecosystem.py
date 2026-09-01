import pytest
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal

from app.core.security import get_password_hash
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.services.multilingual.translator import multilingual_service
from app.services.provenance.provenance import provenance_service
from app.services.integrations.mock_broker import mock_broker_adapter


@pytest.fixture
def ecosystem_setup():
    """Ensure database has baseline entities for Phase 8 ecosystem tests."""
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "phase8_tester@mats.ai").first()
        if not user:
            user = User(
                email="phase8_tester@mats.ai",
                hashed_password=get_password_hash("Secret123!"),
                full_name="Phase 8 Tester",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Ensure portfolio exists
        port = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        if not port:
            port = Portfolio(user_id=user.id, name="Phase 8 Test Portfolio", cash_balance=10000.0)
            db.add(port)
            db.commit()
            db.refresh(port)

        return user.id, port.id
    finally:
        db.close()


def get_auth_headers(client: TestClient) -> dict:
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "phase8_tester@mats.ai", "password": "Secret123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. Multilingual Intelligence & Glossary Protection Tests
def test_multilingual_language_detection():
    assert multilingual_service.detect_language("Why did my risk increase?") == "en"
    assert multilingual_service.detect_language("என் போர்ட்ஃபோலியோ அபாயம் ஏன் அதிகரித்தது?") == "ta"
    assert multilingual_service.detect_language("मेरे पोर्टफोलियो का जोखिम क्यों बढ़ गया?") == "hi"


def test_multilingual_financial_glossary_protection():
    ta_vol = multilingual_service.translate_concept("volatility", "ta")
    assert "Volatility" in ta_vol
    assert "அதிர்வுத்தன்மை" in ta_vol

    hi_risk = multilingual_service.translate_concept("risk level", "hi")
    assert "Risk Level" in hi_risk
    assert "जोखिम स्तर" in hi_risk


def test_multilingual_localization_preserves_metrics():
    summary = "Portfolio risk score is 68.5% with NVDA trading at $128.50 on 2024-09-01."
    key_findings = ["RSI is 64.2 with BULLISH momentum", "Concentration at 42.0%"]
    risks = ["Downside drawdown potential of 15.4%"]
    counterargs = ["Operating margin expansion may slow"]
    follow_ups = ["Explain risk"]

    loc = multilingual_service.localize_copilot_response(
        summary=summary,
        key_findings=key_findings,
        risks=risks,
        counterarguments=counterargs,
        follow_ups=follow_ups,
        target_lang="ta",
    )

    # Verify numbers, symbols, and tickers are strictly intact
    assert "68.5%" in loc["summary"]
    assert "$128.50" in loc["summary"]
    assert "NVDA" in loc["summary"]
    assert "2024-09-01" in loc["summary"]
    assert "[தமிழ் அறிக்கை]" in loc["summary"]


# 2. Multilingual Copilot Route Test
def test_copilot_multilingual_chat(client: TestClient, ecosystem_setup):
    headers = get_auth_headers(client)
    payload = {
        "message": "என் போர்ட்ஃபோலியோ அபாயத்தை பகுப்பாய்வு செய்யுங்கள்",
        "language": "ta",
    }
    r = client.post("/api/v1/copilot/chat", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["language"] == "ta"
    assert "அறிக்கை" in data["summary"] or "போர்ட்ஃபோலியோ" in data["summary"]
    assert len(data["follow_ups"]) > 0


# 3. Data Provenance Schema & Hierarchy Tests
def test_data_provenance_schema():
    prov = provenance_service.create_provenance(
        source="SEC EDGAR 10-K",
        provider="sec_edgar",
        data_type="OFFICIAL_FILING",
        hierarchy="OFFICIAL",
        confidence=0.98,
    )
    assert prov.source_hierarchy == "OFFICIAL"
    assert prov.confidence == 0.98
    assert prov.freshness == "RECENT"


# 4. Source Conflict Detection Tests
def test_source_conflict_detection_divergence():
    source_a = {"name": "Primary Feed", "value": 128.50, "hierarchy": "PRIMARY"}
    source_b = {"name": "Secondary Feed", "value": 133.00, "hierarchy": "SECONDARY"}

    report = provenance_service.detect_source_conflict("NVDA", "Price", source_a, source_b)
    assert report.has_conflict is True
    assert report.status == "SOURCE_CONFLICT_DETECTED"
    assert "divergence" in report.interpretation.lower()


def test_source_conflict_detection_consistent():
    source_a = {"name": "Primary Feed", "value": 128.50, "hierarchy": "PRIMARY"}
    source_b = {"name": "Secondary Feed", "value": 128.60, "hierarchy": "SECONDARY"}

    report = provenance_service.detect_source_conflict("NVDA", "Price", source_a, source_b)
    assert report.has_conflict is False
    assert report.status == "CONSISTENT"


# 5. Data Lineage Chain Tests
def test_data_lineage_chain():
    nodes = provenance_service.get_data_lineage(
        conclusion_title="Elevated Concentration Risk",
        agent_name="Risk",
        finding_summary="Single holding exceeds 40%",
        metric_name="NVDA Weight",
        metric_value="42.5%",
        source_title="Primary Portfolio Telemetry",
        provider_name="MATS Normalization Service",
        hierarchy="PRIMARY",
    )
    assert len(nodes) == 4
    levels = [n.level for n in nodes]
    assert levels == ["CONCLUSION", "AGENT_FINDING", "METRIC", "SOURCE"]


# 6. Portfolio CSV Import with Row Validation Tests
def test_portfolio_csv_import_validation(client: TestClient, ecosystem_setup):
    _, port_id = ecosystem_setup
    headers = get_auth_headers(client)
    csv_payload = {
        "csv_content": (
            "symbol,quantity,average_price\n"
            "NVDA,15,122.50\n"
            "MSFT,10,412.00\n"
            "MALFORMED_ROW,-5,0\n"
            "INVALID!@#$,10,150.00\n"
            "AAPL,20,195.00"
        )
    }

    r = client.post(f"/api/v1/portfolio/{port_id}/import-csv", json=csv_payload, headers=headers)
    assert r.status_code == 200
    data = r.json()

    assert data["valid_count"] == 3  # NVDA, MSFT, AAPL
    assert data["rejected_count"] == 2  # MALFORMED_ROW, INVALID!@#$
    assert len(data["valid_rows"]) == 3
    assert len(data["rejected_rows"]) == 2


# 7. User Data Portability Export & IDOR Defense
def test_user_data_export_json_and_csv(client: TestClient, ecosystem_setup):
    user_id, _ = ecosystem_setup
    headers = get_auth_headers(client)

    # Test JSON export
    r_json = client.get("/api/v1/ecosystem/export?format=json", headers=headers)
    assert r_json.status_code == 200
    data = r_json.json()
    assert data["user_profile"]["id"] == user_id
    assert "portfolios" in data
    assert "watchlists" in data

    # Test CSV export
    r_csv = client.get("/api/v1/ecosystem/export?format=csv", headers=headers)
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers["content-type"]
    assert "Portfolio" in r_csv.text


# 8. Mock Brokerage Sync & Read-Only Non-Custodial Enforcement
def test_mock_broker_read_only_sync_and_prohibition(client: TestClient, ecosystem_setup):
    headers = get_auth_headers(client)
    r = client.post("/api/v1/ecosystem/broker/sync", json={"account_id": "ACC-DEMO-9942"}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["is_read_only"] is True
    assert data["synced_holdings_count"] > 0
    assert "DEMO DATA" in data["disclaimer"]

    # Verify trade execution strictly raises PermissionError
    with pytest.raises(PermissionError) as exc_info:
        mock_broker_adapter.execute_order("BUY", "NVDA", 10)
    assert "Trade execution prohibited" in str(exc_info.value)


# 9. User Feedback Collection & Analytics Tests
def test_user_feedback_and_impact_metrics(client: TestClient, ecosystem_setup):
    headers = get_auth_headers(client)
    fb_payload = {
        "target_type": "COPILOT_MESSAGE",
        "target_id": "msg-999",
        "is_helpful": True,
        "comment": "Accurate SEC citations and counterarguments.",
    }
    r_fb = client.post("/api/v1/ecosystem/feedback", json=fb_payload, headers=headers)
    assert r_fb.status_code == 200
    assert r_fb.json()["status"] == "SUCCESS"

    # Check analytics
    r_ana = client.get("/api/v1/ecosystem/feedback/analytics", headers=headers)
    assert r_ana.status_code == 200
    assert r_ana.json()["total_feedbacks"] >= 1

    # Check impact metrics
    r_imp = client.get("/api/v1/ecosystem/impact", headers=headers)
    assert r_imp.status_code == 200
    imp = r_imp.json()
    assert imp["languages_supported_count"] == 3
    assert imp["time_savings_metric_type"] == "ESTIMATE"


# 10. Accessibility Preferences CRUD
def test_accessibility_preferences_crud(client: TestClient, ecosystem_setup):
    headers = get_auth_headers(client)
    # Get current
    r_get = client.get("/api/v1/ecosystem/accessibility", headers=headers)
    assert r_get.status_code == 200

    # Update preferences
    update_payload = {
        "language": "ta",
        "text_size": "large",
        "high_contrast": True,
        "reduced_motion": True,
    }
    r_put = client.put("/api/v1/ecosystem/accessibility", json=update_payload, headers=headers)
    assert r_put.status_code == 200
    prefs = r_put.json()["preferences"]
    assert prefs["language"] == "ta"
    assert prefs["text_size"] == "large"
    assert prefs["high_contrast"] is True
    assert prefs["reduced_motion"] is True


# 11. Contextual Educational Concepts
def test_contextual_education_endpoint(client: TestClient, ecosystem_setup):
    headers = get_auth_headers(client)
    r = client.get("/api/v1/ecosystem/education/volatility", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "Volatility" in data["title"]
    assert "simple_definition" in data
    assert "example" in data
    assert "limitations" in data
    assert "EDUCATIONAL EXPLANATION ONLY" in data["disclaimer"]
