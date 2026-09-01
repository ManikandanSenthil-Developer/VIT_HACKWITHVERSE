from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentIngestRequest(BaseModel):
    title: str
    company_symbol: str
    document_type: str = "10-K"  # 10-K, 10-Q, 8-K, Presentation, Disclosure
    content: Optional[str] = None  # Direct textual content
    source_url: Optional[str] = None  # Validated external filing URL
    source_identifier: Optional[str] = None
    publication_date: Optional[datetime] = None


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    text: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: int
    title: str
    company_symbol: str
    document_type: str
    source_url: Optional[str] = None
    source_identifier: Optional[str] = None
    publication_date: Optional[datetime] = None
    retrieval_date: datetime
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagSearchRequest(BaseModel):
    query: str
    symbol: Optional[str] = None
    document_type: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: Optional[float] = None  # Defaults to settings.RAG_SIMILARITY_THRESHOLD


class RagCitation(BaseModel):
    document_id: int
    document_title: str
    company_symbol: str
    document_type: str
    source_url: Optional[str] = None
    publication_date: Optional[datetime] = None
    section: Optional[str] = None
    page_number: Optional[int] = None


class RagSearchResultItem(BaseModel):
    text: str
    score: float
    source: str
    document: str
    metadata: Dict[str, Any]
    citation: RagCitation


class RagSearchResponse(BaseModel):
    query: str
    results_found: bool
    results: List[RagSearchResultItem]
    message: Optional[str] = None  # "No reliable supporting evidence was found." when empty
    query_latency_ms: float
