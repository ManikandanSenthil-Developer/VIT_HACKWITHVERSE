from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.document import Document
from app.models.user import User
from app.schemas.rag import (
    DocumentIngestRequest,
    DocumentResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.services.documents.ingest_service import ingestion_service
from app.services.retrieval.vector_search import vector_search_service

router = APIRouter()


from app.core.rate_limiter import rate_limit_dependency
from app.services.audit.audit_service import audit_service


@router.post(
    "/ingest",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency(max_requests=15, window_seconds=60, by_user=True, action="rag_ingest"))],
)
async def ingest_document(
    request: DocumentIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Ingest, parse, chunk, and embed official financial filing or document.
    Enforces SSRF safety and size quotas.
    """
    try:
        doc = await ingestion_service.ingest_document(db, req=request)
        audit_service.log_event(
            db=db,
            action="DOCUMENT_INGESTION",
            user_id=current_user.id,
            resource_type="Document",
            resource_id=str(doc.id),
            details={"title": doc.title, "symbol": doc.company_symbol, "document_type": doc.document_type},
            status="SUCCESS",
        )
        return doc
    except ValueError as e:
        audit_service.log_event(
            db=db,
            action="DOCUMENT_INGESTION",
            user_id=current_user.id,
            resource_type="Document",
            details={"title": request.title, "symbol": request.company_symbol, "error": str(e)},
            status="FAILURE",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        audit_service.log_event(
            db=db,
            action="DOCUMENT_INGESTION",
            user_id=current_user.id,
            resource_type="Document",
            details={"title": request.title, "symbol": request.company_symbol, "error": str(e)},
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}",
        )


@router.post("/search", response_model=RagSearchResponse)
async def search_knowledge(
    request: RagSearchRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Perform semantic vector search across ingested financial filings.
    Enforces similarity threshold, metadata filtering, and strict 'no evidence' fallback.
    """
    return await vector_search_service.search(db, request=request)


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    symbol: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Any:
    """List ingested knowledge documents with status and chunk counts."""
    query = db.query(Document)
    if symbol:
        query = query.filter(Document.company_symbol == symbol.upper())
    if document_type:
        query = query.filter(Document.document_type == document_type)
    return query.order_by(Document.created_at.desc()).limit(limit).all()


@router.get("/document/{document_id}", response_model=DocumentResponse)
def get_document_by_id(
    document_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve details and metadata for a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc
