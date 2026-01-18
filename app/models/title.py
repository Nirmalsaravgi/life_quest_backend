"""
Title & Achievement Models

Handles unlockable titles and achievements.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class Title(Base, UUIDMixin):
    """
    Unlockable titles/achievements.
    """

    __tablename__ = "titles"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unlock_condition: Mapped[str] = mapped_column(String(50), nullable=False)  # streak_days, level_reached
    unlock_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user_titles: Mapped[list["UserTitle"]] = relationship("UserTitle", back_populates="title")


class UserTitle(Base, UUIDMixin):
    """
    Earned titles by users.
    """

    __tablename__ = "user_titles"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    earned_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    title: Mapped["Title"] = relationship("Title", back_populates="user_titles")
