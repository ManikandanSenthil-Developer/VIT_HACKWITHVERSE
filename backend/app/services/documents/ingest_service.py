from datetime import datetime, timezone
import hashlib
import json
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from app.core.security_validation import validate_safe_url, validate_document_size, sanitize_symbol
from app.models.document import Document, DocumentChunk
from app.schemas.rag import DocumentIngestRequest, DocumentResponse
from app.services.documents.parser import DocumentParser
from app.services.documents.chunker import DocumentChunker
from app.services.embeddings.embedding_service import embedding_service


class IngestionService:
    def __init__(self):
        self.chunker = DocumentChunker()

    async def ingest_document(self, db: Session, req: DocumentIngestRequest) -> DocumentResponse:
        sym = sanitize_symbol(req.company_symbol)
        raw_text = req.content or ""

        # 1. If content is empty and source_url is provided, download with SSRF protection
        if req.source_url and not raw_text.strip():
            safe_url = validate_safe_url(req.source_url)
            headers = {"User-Agent": "MATS-Financial-Intelligence/1.0 (contact@mats.ai)"}
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                resp = await client.get(safe_url, headers=headers)
                resp.raise_for_status()
                validate_document_size(len(resp.content))

                content_type = resp.headers.get("content-type", "").lower()
                if "pdf" in content_type or safe_url.endswith(".pdf"):
                    raw_text, _ = DocumentParser.parse_pdf(resp.content)
                elif "html" in content_type or safe_url.endswith(".html") or safe_url.endswith(".htm"):
                    raw_text = DocumentParser.parse_html(resp.text)
                else:
                    raw_text = DocumentParser.clean_text(resp.text)
        elif req.source_url:
            validate_safe_url(req.source_url)
            raw_text = DocumentParser.auto_parse(raw_text)
        else:
            raw_text = DocumentParser.auto_parse(raw_text)

        if not raw_text.strip():
            raise ValueError("Document content is empty or could not be parsed.")

        validate_document_size(len(raw_text.encode("utf-8")))

        # 2. Deduplication check via SHA-256
        file_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        existing = db.query(Document).filter(Document.file_hash == file_hash).first()
        if existing:
            return DocumentResponse.model_validate(existing)

        # 3. Create Document DB entity
        doc = Document(
            title=req.title,
            company_symbol=sym,
            document_type=req.document_type,
            source_url=req.source_url,
            source_identifier=req.source_identifier or f"DOC-{sym}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            publication_date=req.publication_date or datetime.now(timezone.utc),
            retrieval_date=datetime.now(timezone.utc),
            file_hash=file_hash,
            raw_content=raw_text[:50000],  # Keep reasonable snippet
            status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # 4. Chunk document
            meta = {
                "document_id": doc.id,
                "title": doc.title,
                "symbol": doc.company_symbol,
                "document_type": doc.document_type,
                "source_url": doc.source_url,
            }
            chunks = self.chunker.chunk_document(raw_text, document_metadata=meta)

            if not chunks:
                doc.status = "failed"
                doc.error_message = "No semantic chunks generated."
                db.commit()
                return DocumentResponse.model_validate(doc)

            # 5. Generate embeddings in batch
            chunk_texts = [c["text"] for c in chunks]
            embeddings = await embedding_service.get_embeddings_batch(chunk_texts)

            # 6. Save DocumentChunks
            for i, chunk_data in enumerate(chunks):
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=chunk_data["chunk_index"],
                    text=chunk_data["text"],
                    section=chunk_data.get("section"),
                    page_number=chunk_data.get("page_number"),
                    embedding_json=json.dumps(embeddings[i]),
                    metadata_json=json.dumps(chunk_data["metadata"]),
                )
                db.add(chunk_obj)

            doc.chunk_count = len(chunks)
            doc.status = "processed"
            db.commit()
            db.refresh(doc)

        except Exception as e:
            doc.status = "failed"
            doc.error_message = str(e)
            db.commit()
            raise e

        return DocumentResponse.model_validate(doc)


ingestion_service = IngestionService()
