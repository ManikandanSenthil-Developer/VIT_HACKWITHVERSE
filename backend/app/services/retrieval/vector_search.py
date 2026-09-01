import json
import time
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.schemas.rag import (
    RagSearchRequest,
    RagSearchResponse,
    RagSearchResultItem,
    RagCitation,
)
from app.services.embeddings.embedding_service import embedding_service


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class VectorSearchService:
    @staticmethod
    async def search(
        db: Session,
        request: RagSearchRequest,
    ) -> RagSearchResponse:
        start_time = time.time()
        query = request.query.strip()
        threshold = (
            request.similarity_threshold
            if request.similarity_threshold is not None
            else settings.RAG_SIMILARITY_THRESHOLD
        )

        if not query:
            return RagSearchResponse(
                query=query,
                results_found=False,
                results=[],
                message="No reliable supporting evidence was found.",
                query_latency_ms=0.0,
            )

        # 1. Embed query
        query_vector = await embedding_service.get_embedding(query)

        # 2. Build filtered SQL query
        db_query = db.query(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id)
        if request.symbol:
            db_query = db_query.filter(Document.company_symbol == request.symbol.upper())
        if request.document_type:
            db_query = db_query.filter(Document.document_type == request.document_type)

        chunks = db_query.all()

        if not chunks:
            latency = (time.time() - start_time) * 1000
            return RagSearchResponse(
                query=query,
                results_found=False,
                results=[],
                message="No reliable supporting evidence was found.",
                query_latency_ms=round(latency, 2),
            )

        # 3. Compute cosine similarity scores
        scored_items = []
        for chunk in chunks:
            try:
                chunk_vec = json.loads(chunk.embedding_json)
                score = cosine_similarity(query_vector, chunk_vec)
                if score >= threshold:
                    scored_items.append((score, chunk))
            except Exception:
                continue

        # Sort descending by score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_items = scored_items[: request.top_k]

        latency = (time.time() - start_time) * 1000

        # Strict RAG Quality Rule: If no evidence satisfies similarity threshold
        if not top_items:
            return RagSearchResponse(
                query=query,
                results_found=False,
                results=[],
                message="No reliable supporting evidence was found.",
                query_latency_ms=round(latency, 2),
            )

        # 4. Format structured result items with full source citations
        results: List[RagSearchResultItem] = []
        for score, chunk in top_items:
            doc = chunk.document
            meta = json.loads(chunk.metadata_json) if chunk.metadata_json else {}

            citation = RagCitation(
                document_id=doc.id,
                document_title=doc.title,
                company_symbol=doc.company_symbol,
                document_type=doc.document_type,
                source_url=doc.source_url,
                publication_date=doc.publication_date,
                section=chunk.section,
                page_number=chunk.page_number,
            )

            results.append(
                RagSearchResultItem(
                    text=chunk.text,
                    score=round(score, 4),
                    source=doc.source_url or doc.source_identifier or f"Doc #{doc.id}",
                    document=doc.title,
                    metadata=meta,
                    citation=citation,
                )
            )

        return RagSearchResponse(
            query=query,
            results_found=True,
            results=results,
            message=None,
            query_latency_ms=round(latency, 2),
        )


vector_search_service = VectorSearchService()
