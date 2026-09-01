import pytest
from app.services.documents.chunker import DocumentChunker
from app.services.documents.parser import DocumentParser


SAMPLE_FILING_TEXT = """
Item 1. Business Overview
--- [Page 1] ---
NVIDIA Corporation is a global leader in accelerated computing and artificial intelligence architectures.
Our Compute & Networking segment includes our Data Center accelerated computing platform.

Item 1A. Risk Factors
--- [Page 12] ---
Failure to meet the rapid demand for high-bandwidth memory (HBM) and advanced CoWoS packaging could adversely
impact our delivery schedules for Blackwell GPU platforms and gross margins.

Item 7. Management's Discussion and Analysis
--- [Page 28] ---
Data Center revenue for fiscal year 2024 was $47.5 billion, up 217% compared to the prior year.
Growth was driven by the NVIDIA HGX platform and cloud hyperscaler demand for generative AI training.
"""


def test_document_chunking():
    chunker = DocumentChunker(target_chunk_size=300, overlap=50)
    meta = {"symbol": "NVDA", "document_type": "10-K"}
    chunks = chunker.chunk_document(SAMPLE_FILING_TEXT, meta)
    assert len(chunks) >= 2
    # Verify section and page retention
    sections = [c["section"] for c in chunks]
    assert any("Business" in s or "Risk Factors" in s or "Management" in s for s in sections)
    pages = [c["page_number"] for c in chunks]
    assert any(p in (1, 12, 28) for p in pages)


def test_document_ingestion_and_search_flow(client):
    # 1. Register and get auth token for protected /rag/ingest endpoint
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "rag_analyst@mats.ai",
        "password": "SecurePassword123!",
        "full_name": "RAG Research Lead"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest document
    ingest_payload = {
        "title": "NVIDIA 2024 Annual 10-K Report",
        "company_symbol": "NVDA",
        "document_type": "10-K",
        "content": SAMPLE_FILING_TEXT,
        "source_url": "https://sec.gov/edgar/data/1045810/nvda-202410k.htm",
        "source_identifier": "SEC-EDGAR-0001045810-24-000029",
    }
    ingest_res = client.post("/api/v1/rag/ingest", json=ingest_payload, headers=headers)
    assert ingest_res.status_code == 201
    doc_data = ingest_res.json()
    assert doc_data["company_symbol"] == "NVDA"
    assert doc_data["chunk_count"] > 0
    assert doc_data["status"] == "processed"

    # 3. Test Deduplication
    ingest_dup_res = client.post("/api/v1/rag/ingest", json=ingest_payload, headers=headers)
    assert ingest_dup_res.status_code == 201
    assert ingest_dup_res.json()["id"] == doc_data["id"]

    # 4. Search query with high relevance
    search_res = client.post("/api/v1/rag/search", json={
        "query": "What was the Data Center revenue growth driven by generative AI?",
        "symbol": "NVDA",
        "top_k": 3,
        "similarity_threshold": 0.15,
    })
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["results_found"] is True
    assert len(search_data["results"]) > 0
    top_result = search_data["results"][0]
    assert top_result["score"] > 0.15
    assert "Data Center" in top_result["text"]

    # Verify citation fields
    citation = top_result["citation"]
    assert citation["document_title"] == "NVIDIA 2024 Annual 10-K Report"
    assert citation["company_symbol"] == "NVDA"
    assert "sec.gov" in citation["source_url"]

    # 5. Strict RAG Quality Rule: Test query with completely disjoint irrelevant query
    unrelated_search = client.post("/api/v1/rag/search", json={
        "query": "Who won the medieval Roman gladiator championship in year 1200?",
        "symbol": "NVDA",
        "top_k": 3,
        "similarity_threshold": 0.85,  # High threshold impossible to satisfy
    })
    assert unrelated_search.status_code == 200
    unrelated_data = unrelated_search.json()
    assert unrelated_data["results_found"] is False
    assert len(unrelated_data["results"]) == 0
    assert unrelated_data["message"] == "No reliable supporting evidence was found."
