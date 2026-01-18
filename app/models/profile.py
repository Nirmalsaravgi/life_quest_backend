"""
User Profile & Game Identity Models

Handles player identity, archetypes, and life modes.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Archetype(Base, UUIDMixin):
    """
    Player archetypes that define playstyle.
    
    Options: Explorer, Builder, Strategist, Warrior, Sage
    """

    __tablename__ = "archetypes"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    passive_bonuses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    profiles: Mapped[list["UserProfile"]] = relationship("UserProfile", back_populates="archetype")


class LifeMode(Base, UUIDMixin):
    """
    Operating modes that affect gameplay.
    
    Options: Discipline, Growth, Recovery
    """

    __tablename__ = "life_modes"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    modifiers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    profiles: Mapped[list["UserProfile"]] = relationship("UserProfile", back_populates="life_mode")


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """
    Game identity and progression data.
    
    Created during onboarding after first login.
    """

    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    player_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    archetype_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("archetypes.id"), nullable=True
    )
    life_mode_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("life_modes.id"), nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_core_xp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    identity_locked_until: Mapped[datetime | None] = mapped_column(nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    archetype: Mapped["Archetype | None"] = relationship("Archetype", back_populates="profiles")
    life_mode: Mapped["LifeMode | None"] = relationship("LifeMode", back_populates="profiles")
