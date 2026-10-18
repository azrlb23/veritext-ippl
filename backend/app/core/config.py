from typing import List
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
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # AI & Embedding Engine Parameters
    SENTENCE_TRANSFORMER_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    WINNOWING_K_GRAM: int = 5
    WINNOWING_WINDOW_SIZE: int = 4
    SIMILARITY_LEXICAL_WEIGHT: float = 0.50
    SIMILARITY_SEMANTIC_WEIGHT: float = 0.35
    SIMILARITY_STYLO_WEIGHT: float = 0.15

    # Payment Gateway (Midtrans)
    MIDTRANS_SERVER_KEY: str = "SB-Mid-server-DemoServerKey1234567890"
    MIDTRANS_CLIENT_KEY: str = "SB-Mid-client-DemoClientKey1234567890"
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_MERCHANT_ID: str = "G123456789"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    STORAGE_BACKEND: str = "local"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt"

    # CORS
    CORS_ORIGINS: List[str] = [
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
