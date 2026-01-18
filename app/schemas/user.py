"""
User Schemas

Pydantic models for user request/response.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User response without sensitive data."""

    id: UUID
    email: EmailStr
    email_verified: bool
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """User update request (limited fields)."""

    email: EmailStr | None = None
