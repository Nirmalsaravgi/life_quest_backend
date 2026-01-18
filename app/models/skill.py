"""
Skill Trees & Skills Models

Handles skill progression within life areas.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class SkillTree(Base, UUIDMixin):
    """
    Skill trees within each life area.
    
    Example: Fitness area has Consistency, Strength, Endurance trees.
    """

    __tablename__ = "skill_trees"

    life_area_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("life_areas.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    life_area: Mapped["LifeArea"] = relationship("LifeArea", back_populates="skill_trees")
    skills: Mapped[list["Skill"]] = relationship("Skill", back_populates="skill_tree")


class Skill(Base, UUIDMixin):
    """
    Individual skills within trees.
    
    Unlocking provides passive buffs and new features.
    """

    __tablename__ = "skills"

    skill_tree_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("skill_trees.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tier: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5
    unlock_cost: Mapped[int] = mapped_column(Integer, nullable=False)  # Skill XP required
    passive_effects: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    skill_tree: Mapped["SkillTree"] = relationship("SkillTree", back_populates="skills")
    user_skills: Mapped[list["UserSkill"]] = relationship("UserSkill", back_populates="skill")
    prerequisites: Mapped[list["SkillPrerequisite"]] = relationship(
        "SkillPrerequisite", 
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill"
    )


class SkillPrerequisite(Base, UUIDMixin):
    """
    Skill dependency graph.
    
    Defines which skills must be unlocked before another.
    """

    __tablename__ = "skill_prerequisites"

    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    prerequisite_skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    skill: Mapped["Skill"] = relationship(
        "Skill", foreign_keys=[skill_id], back_populates="prerequisites"
    )
    prerequisite: Mapped["Skill"] = relationship("Skill", foreign_keys=[prerequisite_skill_id])


class UserSkill(Base, UUIDMixin):
    """
    User's unlocked/progressed skills.
    """

    __tablename__ = "user_skills"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    current_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    skill_xp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills")


# Import for type hints
from app.models.life_area import LifeArea  # noqa: E402, F401
