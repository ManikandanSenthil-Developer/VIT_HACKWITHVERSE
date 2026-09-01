import pytest
from fastapi import HTTPException
from app.core.security_validation import validate_safe_url, sanitize_symbol, validate_document_size


def test_sanitize_symbol_valid_and_invalid():
    assert sanitize_symbol("nvda") == "NVDA"
    assert sanitize_symbol("  brk.b ") == "BRK.B"
    assert sanitize_symbol("bf-b") == "BF-B"

    with pytest.raises(HTTPException) as exc:
        sanitize_symbol("NVDA; DROP TABLE users;")
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException):
        sanitize_symbol("AAPL Ticker")


def test_ssrf_url_validation():
    # Valid external HTTPS URL
    assert validate_safe_url("https://sec.gov/edgar/data/1045810/nvda.htm") == "https://sec.gov/edgar/data/1045810/nvda.htm"

    # Localhost blocking
    with pytest.raises(HTTPException) as exc1:
        validate_safe_url("http://localhost:8000/internal")
    assert exc1.value.status_code == 400

    with pytest.raises(HTTPException) as exc2:
        validate_safe_url("http://127.0.0.1:5432/mats")
    assert exc2.value.status_code == 400

    # AWS/Cloud Metadata blocking
    with pytest.raises(HTTPException) as exc3:
        validate_safe_url("http://169.254.169.254/latest/meta-data")
    assert exc3.value.status_code == 400

    # Non-HTTP/HTTPS schemes
    with pytest.raises(HTTPException) as exc4:
        validate_safe_url("file:///etc/passwd")
    assert exc4.value.status_code == 400


def test_document_size_limit():
    # 5 MB is fine
    validate_document_size(5 * 1024 * 1024)

    # 15 MB exceeds 10MB limit
    with pytest.raises(HTTPException) as exc:
        validate_document_size(15 * 1024 * 1024)
    assert exc.value.status_code == 413


def test_protected_ingest_unauthenticated(client):
    res = client.post("/api/v1/rag/ingest", json={
        "title": "Unauthorized Document",
        "company_symbol": "NVDA",
        "content": "Secret information",
    })
    # Must reject without valid Bearer token
    assert res.status_code == 401
