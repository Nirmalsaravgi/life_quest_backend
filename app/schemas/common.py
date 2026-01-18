"""
Common Schemas

Shared Pydantic models used across the API.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail in response."""

    type: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(BaseModel):
    """Simple success response."""

    success: bool = True
    message: str = "Operation completed successfully"
