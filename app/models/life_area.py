"""
Life Areas Models

Defines the six core life domains and user selections.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class LifeArea(Base, UUIDMixin):
    """
    Six core life domains.
    
    Examples: Mind 🧠, Body 💪, Career 💼, Finance 💰, etc.
    """

    __tablename__ = "life_areas"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user_life_areas: Mapped[list["UserLifeArea"]] = relationship(
        "UserLifeArea", back_populates="life_area"
    )
    skill_trees: Mapped[list["SkillTree"]] = relationship(
        "SkillTree", back_populates="life_area"
    )


class UserLifeArea(Base, UUIDMixin):
    """
    Junction table for user's selected life areas.
    
    Users can select up to 3 active life areas.
    """

    __tablename__ = "user_life_areas"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    life_area_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("life_areas.id", ondelete="CASCADE"), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3
    selected_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    life_area: Mapped["LifeArea"] = relationship("LifeArea", back_populates="user_life_areas")


# Forward reference for SkillTree
from app.models.skill import SkillTree  # noqa: E402, F401
