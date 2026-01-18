"""
Quest Models

Handles quests, quest types, and completions.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class QuestType(Base, UUIDMixin):
    """
    Quest categorization.
    
    Types: main, daily, side, hidden
    """

    __tablename__ = "quest_types"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    quests: Mapped[list["Quest"]] = relationship("Quest", back_populates="quest_type")


class Quest(Base, UUIDMixin, TimestampMixin):
    """
    User quests - both user-created and system-generated.
    """

    __tablename__ = "quests"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quest_type_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("quest_types.id"), nullable=False
    )
    life_area_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("life_areas.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    # Relationships
    quest_type: Mapped["QuestType"] = relationship("QuestType", back_populates="quests")
    completions: Mapped[list["QuestCompletion"]] = relationship(
        "QuestCompletion", back_populates="quest"
    )


class QuestCompletion(Base, UUIDMixin):
    """
    Quest completion records with earned rewards.
    """

    __tablename__ = "quest_completions"

    quest_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("quests.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_multiplier: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0, nullable=False)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    quest: Mapped["Quest"] = relationship("Quest", back_populates="completions")
