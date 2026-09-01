import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    PROJECT_NAME: str = "MATS - Multi-Agent Autonomous Financial Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET: str = "mats_jwt_super_secret_key_change_in_production_2026"
    JWT_REFRESH_SECRET: str = "mats_refresh_super_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    # Supports PostgreSQL as required, with fallback to SQLite for immediate local testing if PostgreSQL service is offline
    DATABASE_URL: str = "sqlite:///./mats.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    # Phase 2: Caching TTLs (seconds)
    CACHE_QUOTE_TTL_SECONDS: int = 60
    CACHE_HISTORY_TTL_SECONDS: int = 3600
    CACHE_FUNDAMENTALS_TTL_SECONDS: int = 86400
    CACHE_COMPANY_TTL_SECONDS: int = 86400

    # Phase 2: Market Data Providers
    MARKET_DATA_PROVIDER: str = "hybrid"  # hybrid, yahoo, mock
    FINNHUB_API_KEY: Union[str, None] = None

    # Phase 2: RAG & Embeddings
    EMBEDDING_PROVIDER: str = "local"  # local, openai
    OPENAI_API_KEY: Union[str, None] = None
    RAG_SIMILARITY_THRESHOLD: float = 0.25
    RAG_TOP_K: int = 5
    MAX_DOCUMENT_SIZE_BYTES: int = 10485760  # 10MB


settings = Settings()
