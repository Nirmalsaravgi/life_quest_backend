"""
Profile Repository

Data access layer for profile, archetype, and life area operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.life_area import LifeArea, UserLifeArea
from app.models.profile import Archetype, LifeMode, UserProfile


class ProfileRepository:
    """Repository for profile-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Profile Operations ====================

    async def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        """Get a profile by user ID."""
        result = await self.db.execute(
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                selectinload(UserProfile.archetype),
                selectinload(UserProfile.life_mode),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_player_name(self, player_name: str) -> UserProfile | None:
        """Get a profile by player name."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.player_name == player_name)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: UUID,
        player_name: str,
        archetype_id: UUID | None = None,
        life_mode_id: UUID | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
        timezone_str: str = "UTC",
    ) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(
            user_id=user_id,
            player_name=player_name,
            archetype_id=archetype_id,
            life_mode_id=life_mode_id,
            avatar_url=avatar_url,
            bio=bio,
            timezone=timezone_str,
            level=1,
            total_core_xp=0,
            onboarding_completed=False,
        )
        self.db.add(profile)
        await self.db.flush()
        
        # Reload with relationships
        await self.db.refresh(profile, ["archetype", "life_mode"])
        return profile

    async def update(
        self,
        profile: UserProfile,
        player_name: str | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
        timezone_str: str | None = None,
    ) -> UserProfile:
        """Update a user profile."""
        if player_name is not None:
            profile.player_name = player_name
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if bio is not None:
            profile.bio = bio
        if timezone_str is not None:
            profile.timezone = timezone_str
        
        await self.db.flush()
        return profile

    async def mark_onboarding_complete(self, profile: UserProfile) -> None:
        """Mark onboarding as completed and lock identity."""
        from datetime import timedelta
        
        profile.onboarding_completed = True
        profile.identity_locked_until = datetime.now(timezone.utc) + timedelta(days=30)
        await self.db.flush()

    # ==================== Archetype Operations ====================

    async def get_all_archetypes(self) -> list[Archetype]:
        """Get all archetypes."""
        result = await self.db.execute(select(Archetype))
        return list(result.scalars().all())

    async def get_archetype_by_id(self, archetype_id: UUID) -> Archetype | None:
        """Get an archetype by ID."""
        result = await self.db.execute(
            select(Archetype).where(Archetype.id == archetype_id)
        )
        return result.scalar_one_or_none()

    # ==================== Life Mode Operations ====================

    async def get_all_life_modes(self) -> list[LifeMode]:
        """Get all life modes."""
        result = await self.db.execute(select(LifeMode))
        return list(result.scalars().all())

    async def get_life_mode_by_id(self, life_mode_id: UUID) -> LifeMode | None:
        """Get a life mode by ID."""
        result = await self.db.execute(
            select(LifeMode).where(LifeMode.id == life_mode_id)
        )
        return result.scalar_one_or_none()

    # ==================== Life Area Operations ====================

    async def get_all_life_areas(self) -> list[LifeArea]:
        """Get all active life areas."""
        result = await self.db.execute(
            select(LifeArea).where(LifeArea.is_active == True)
        )
        return list(result.scalars().all())

    async def get_life_area_by_id(self, life_area_id: UUID) -> LifeArea | None:
        """Get a life area by ID."""
        result = await self.db.execute(
            select(LifeArea).where(LifeArea.id == life_area_id)
        )
        return result.scalar_one_or_none()

    async def get_user_life_areas(self, user_id: UUID) -> list[UserLifeArea]:
        """Get user's selected life areas."""
        result = await self.db.execute(
            select(UserLifeArea)
            .where(UserLifeArea.user_id == user_id)
            .order_by(UserLifeArea.priority)
        )
        return list(result.scalars().all())

    async def set_user_life_areas(
        self, user_id: UUID, life_area_ids: list[UUID]
    ) -> list[UserLifeArea]:
        """Set user's selected life areas (replaces existing)."""
        # Delete existing selections
        existing = await self.get_user_life_areas(user_id)
        for ula in existing:
            await self.db.delete(ula)
        
        # Create new selections
        user_life_areas = []
        for priority, life_area_id in enumerate(life_area_ids, start=1):
            ula = UserLifeArea(
                user_id=user_id,
                life_area_id=life_area_id,
                priority=priority,
                selected_at=datetime.now(timezone.utc),
            )
            self.db.add(ula)
            user_life_areas.append(ula)
        
        await self.db.flush()
        return user_life_areas
