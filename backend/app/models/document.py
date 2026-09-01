from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company_symbol = Column(String(20), index=True, nullable=False)
    document_type = Column(String(50), default="10-K")  # 10-K, 10-Q, 8-K, Presentation, Disclosure
    trust_level = Column(String(50), default="OFFICIAL", nullable=False)  # PRIMARY, OFFICIAL, SECONDARY, TERTIARY, UNKNOWN
    source_url = Column(String(1000), nullable=True)
    source_identifier = Column(String(255), nullable=True)  # e.g. SEC-EDGAR-0001045810-24-000029
    publication_date = Column(DateTime, nullable=True)
    retrieval_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    file_hash = Column(String(64), index=True, nullable=True)  # SHA-256 to prevent duplicate ingestion
    raw_content = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="processed")  # pending, processing, processed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    section = Column(String(255), nullable=True)  # e.g. "Item 1A. Risk Factors"
    page_number = Column(Integer, nullable=True)
    
    # Dense vector representation stored as JSON array of floats for lightweight, zero-daemon laptop storage
    embedding_json = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # Extensible JSON for company, doc type, dates
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_document_chunks_doc_idx", "document_id", "chunk_index"),
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")
