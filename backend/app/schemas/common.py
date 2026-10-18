from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard unified API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    meta: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number, 1-indexed")
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
