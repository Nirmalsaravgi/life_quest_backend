"""
Power-Up Models

Handles power-ups, inventory, and active effects.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class PowerUp(Base, UUIDMixin):
    """
    Available power-ups/boosters.
    """

    __tablename__ = "power_ups"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effect_type: Mapped[str] = mapped_column(String(50), nullable=False)  # xp_multiplier, penalty_shield
    effect_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), default="common", nullable=False)

    # Relationships
    inventory_items: Mapped[list["UserInventory"]] = relationship(
        "UserInventory", back_populates="power_up"
    )
    active_uses: Mapped[list["ActivePowerUp"]] = relationship(
        "ActivePowerUp", back_populates="power_up"
    )


class UserInventory(Base, UUIDMixin):
    """
    User's power-up inventory.
    """

    __tablename__ = "user_inventory"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    power_up_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("power_ups.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    power_up: Mapped["PowerUp"] = relationship("PowerUp", back_populates="inventory_items")


class ActivePowerUp(Base, UUIDMixin):
    """
    Currently active power-up effects.
    """

    __tablename__ = "active_power_ups"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    power_up_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("power_ups.id", ondelete="CASCADE"), nullable=False
    )
    activated_at: Mapped[datetime] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False, index=True)

    # Relationships
    power_up: Mapped["PowerUp"] = relationship("PowerUp", back_populates="active_uses")
