"""
User & Authentication Models

Handles user accounts, OAuth providers, and sessions.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.profile import UserProfile


class User(Base, UUIDMixin, TimestampMixin):
    """
    Core authentication entity.
    
    Handles login credentials and account status.
    Profile/game data is in UserProfile (1:1 relationship).
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False, lazy="selectin"
    )
    auth_providers: Mapped[list["AuthProvider"]] = relationship(
        "AuthProvider", back_populates="user", lazy="selectin"
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", lazy="selectin"
    )


class AuthProvider(Base, UUIDMixin, TimestampMixin):
    """
    OAuth provider connections.
    
    Stores tokens and metadata from Google, Apple, etc.
    """

    __tablename__ = "auth_providers"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'google', 'apple', etc.
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    provider_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="auth_providers")

    # Unique constraint: one provider account per user
    __table_args__ = (
        # UniqueConstraint('provider', 'provider_user_id', name='uq_auth_provider'),
    )


class UserSession(Base, UUIDMixin):
    """
    Active login sessions.
    
    Tracks device info for multi-device support and security.
    """

    __tablename__ = "user_sessions"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    device_info: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
