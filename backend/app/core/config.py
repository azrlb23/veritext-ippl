from __future__ import annotations

from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "VeriText AI API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Security & Tokens
    SECRET_KEY: str = "veritext-ai-super-secret-key-development-minimum-32-chars!"
    JWT_SECRET_KEY: str = "veritext-jwt-signing-secret-key-development-secure-random!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours in development
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database (PostgreSQL + pgvector)
    POSTGRES_USER: str = "veritext"
    POSTGRES_PASSWORD: str = "veritext_secure_pass"
    POSTGRES_DB: str = "veritext_ai"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://veritext:veritext_secure_pass@localhost:5432/veritext_ai"
    SYNC_DATABASE_URL: str = "postgresql://veritext:veritext_secure_pass@localhost:5432/veritext_ai"

    # Redis & Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None  # noqa: UP045
    CELERY_BROKER_URL: Optional[str] = None  # noqa: UP045
    CELERY_RESULT_BACKEND: Optional[str] = None  # noqa: UP045

    @model_validator(mode="after")
    def assemble_redis_urls(self):
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        default_url = f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        if not self.REDIS_URL or self.REDIS_URL == "redis://localhost:6379/0":
            self.REDIS_URL = default_url
        if not self.CELERY_BROKER_URL or self.CELERY_BROKER_URL == "redis://localhost:6379/0":
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND or self.CELERY_RESULT_BACKEND == "redis://localhost:6379/0":
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        return self

    # AI & Embedding Engine Parameters
    SENTENCE_TRANSFORMER_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    HNSW_EF_SEARCH: int = 64
    RERANKER_ENABLED: bool = True
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_THRESHOLD: float = 0.5
    INDOBERT_ENABLED: bool = True
    INDOBERT_MODEL: str = "LazarusNLP/all-indobert-base-v4"
    INDOBERT_MIN_SIM: float = 0.45
    WINNOWING_K_GRAM: int = 5
    WINNOWING_WINDOW_SIZE: int = 4
    SIMILARITY_LEXICAL_WEIGHT: float = 0.50
    SIMILARITY_SEMANTIC_WEIGHT: float = 0.35
    SIMILARITY_STYLO_WEIGHT: float = 0.15
    SIMILARITY_THRESHOLD: float = 0.78
    STYLO_BURSTINESS_THRESHOLD: float = 0.35

    # Gemini AI & Web Plagiarism Scanner (Jalur 1)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    WEB_SCAN_ENABLED: bool = True
    WEB_SCAN_MAX_SENTENCES: int = 120
    WEB_SCAN_TIMEOUT_S: int = 25

    # 9Router DeepSeek Gateway (Dual-Engine LLM)
    ROUTER9_BASE_URL: str = "http://localhost:20128/v1"
    ROUTER9_API_KEY: str = ""
    ROUTER9_MODEL: str = "deepseek/deepseek-v4.1-flash"
    LLM_FAILOVER_STRATEGY: str = "gemini_first"
    LLM_BATCH_MAX_SENTENCES: int = 15

    # OpenRouter API (Free LLM Alternative: Nemotron, Qwen, Gemma)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-lightning:free"

    # Payment Gateway (Midtrans)
    MIDTRANS_SERVER_KEY: str = "SB-Mid-server-DemoServerKey1234567890"
    MIDTRANS_CLIENT_KEY: str = "SB-Mid-client-DemoClientKey1234567890"
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_MERCHANT_ID: str = "G123456789"

    # Google OAuth 2.0 (Google Sign-In)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # SMTP Email Configuration (Password Reset & Notifikasi)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "no-reply@veritext.ai"
    EMAILS_FROM_NAME: str = "VeriText AI"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    STORAGE_BACKEND: str = "local"
    MAX_FILE_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt"

    # Pembatas beban unggahan
    MIN_DOCUMENT_WORDS: int = 50
    MAX_PDF_PAGES: int = 400
    MAX_DOCX_UNCOMPRESSED_MB: int = 50
    MAX_DOCX_COMPRESSION_RATIO: int = 100
    EXTRACTION_TIMEOUT_SECONDS: int = 30
    MAX_ACTIVE_AUDITS_PER_USER: int = 3
    UPLOAD_RATE_LIMIT_PER_MINUTE: int = 10

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
