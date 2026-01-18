"""
XP Models

Handles XP transactions and decay tracking.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin


class UserXP(Base, UUIDMixin):
    """
    Granular XP transactions log.
    
    Append-only for full auditability.
    """

    __tablename__ = "user_xp"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    xp_type: Mapped[str] = mapped_column(String(20), nullable=False)  # core, skill, discipline, courage
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Can be negative for decay
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # quest, streak, bonus, decay
    source_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    earned_at: Mapped[datetime] = mapped_column(nullable=False, index=True)


class XPDecayLog(Base, UUIDMixin):
    """
    Tracks XP penalties for accountability.
    """

    __tablename__ = "xp_decay_log"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    xp_type: Mapped[str] = mapped_column(String(20), nullable=False)
    decay_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)  # missed_quest, inactivity
    decayed_at: Mapped[datetime] = mapped_column(nullable=False)
