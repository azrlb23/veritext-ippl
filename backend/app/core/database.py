from contextlib import contextmanager
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Base Declarative Model Class
Base = declarative_base()

# Asynchronous engine and session for FastAPI endpoints
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.DEBUG and settings.ENVIRONMENT.lower() != "production"),
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous engine for Celery workers & Alembic migrations
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=(settings.DEBUG and settings.ENVIRONMENT.lower() != "production"),
    pool_pre_ping=True,
)


SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing asynchronous database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@contextmanager
def get_sync_db() -> Generator:
    """Context/provider for synchronous database sessions (e.g. Celery workers)."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
