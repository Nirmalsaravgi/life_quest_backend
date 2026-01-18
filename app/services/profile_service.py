"""
Profile Service

Business logic for profile management and onboarding.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundError,
    PlayerNameTakenError,
    ProfileNotFoundError,
    ValidationError,
)
from app.models.profile import UserProfile
from app.repositories.profile_repo import ProfileRepository
from app.schemas.profile import (
    OnboardingRequest,
    OnboardingResponse,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)


class ProfileService:
    """Service for profile operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = ProfileRepository(db)

    async def get_profile(self, user_id: UUID) -> UserProfile:
        """
        Get profile for a user.
        
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError()
        return profile

    async def get_profile_response(self, profile: UserProfile) -> ProfileResponse:
        """Convert profile to response schema."""
        return ProfileResponse.model_validate(profile)

    async def create_profile(
        self, user_id: UUID, data: ProfileCreateRequest
    ) -> UserProfile:
        """
        Create a new profile.
        
        Raises:
            PlayerNameTakenError: If player name is already taken
            ValidationError: If archetype or life mode is invalid
        """
        # Check player name availability
        existing = await self.profile_repo.get_by_player_name(data.player_name)
        if existing:
            raise PlayerNameTakenError()

        # Validate archetype
        archetype = await self.profile_repo.get_archetype_by_id(data.archetype_id)
        if not archetype:
            raise ValidationError("Invalid archetype ID")

        # Validate life mode
        life_mode = await self.profile_repo.get_life_mode_by_id(data.life_mode_id)
        if not life_mode:
            raise ValidationError("Invalid life mode ID")

        # Create profile
        profile = await self.profile_repo.create(
            user_id=user_id,
            player_name=data.player_name,
            archetype_id=data.archetype_id,
            life_mode_id=data.life_mode_id,
            avatar_url=data.avatar_url,
            bio=data.bio,
            timezone_str=data.timezone,
        )

        return profile

    async def update_profile(
        self, user_id: UUID, data: ProfileUpdateRequest
    ) -> UserProfile:
        """
        Update a profile.
        
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            PlayerNameTakenError: If new player name is taken
        """
        profile = await self.get_profile(user_id)

        # Check player name if changing
        if data.player_name and data.player_name != profile.player_name:
            existing = await self.profile_repo.get_by_player_name(data.player_name)
            if existing:
                raise PlayerNameTakenError()

        # Update profile
        profile = await self.profile_repo.update(
            profile=profile,
            player_name=data.player_name,
            avatar_url=data.avatar_url,
            bio=data.bio,
            timezone_str=data.timezone,
        )

        return profile

    async def complete_onboarding(
        self, user_id: UUID, data: OnboardingRequest
    ) -> OnboardingResponse:
        """
        Complete user onboarding - creates profile and sets life areas.
        
        Raises:
            PlayerNameTakenError: If player name is taken
            ValidationError: If any validation fails
        """
        # Check if profile already exists
        existing_profile = await self.profile_repo.get_by_user_id(user_id)
        if existing_profile and existing_profile.onboarding_completed:
            raise ValidationError("Onboarding already completed")

        # Check player name availability
        existing_name = await self.profile_repo.get_by_player_name(data.player_name)
        if existing_name and existing_name.user_id != user_id:
            raise PlayerNameTakenError()

        # Validate archetype
        archetype = await self.profile_repo.get_archetype_by_id(data.archetype_id)
        if not archetype:
            raise ValidationError("Invalid archetype ID")

        # Validate life mode
        life_mode = await self.profile_repo.get_life_mode_by_id(data.life_mode_id)
        if not life_mode:
            raise ValidationError("Invalid life mode ID")

        # Validate life areas
        for life_area_id in data.life_area_ids:
            life_area = await self.profile_repo.get_life_area_by_id(life_area_id)
            if not life_area:
                raise ValidationError(f"Invalid life area ID: {life_area_id}")

        # Create or update profile
        if existing_profile:
            profile = await self.profile_repo.update(
                profile=existing_profile,
                player_name=data.player_name,
                avatar_url=data.avatar_url,
                bio=data.bio,
                timezone_str=data.timezone,
            )
            profile.archetype_id = data.archetype_id
            profile.life_mode_id = data.life_mode_id
        else:
            profile = await self.profile_repo.create(
                user_id=user_id,
                player_name=data.player_name,
                archetype_id=data.archetype_id,
                life_mode_id=data.life_mode_id,
                avatar_url=data.avatar_url,
                bio=data.bio,
                timezone_str=data.timezone,
            )

        # Set life areas
        await self.profile_repo.set_user_life_areas(user_id, data.life_area_ids)

        # Mark onboarding complete
        await self.profile_repo.mark_onboarding_complete(profile)

        # Reload profile with relationships
        profile = await self.profile_repo.get_by_user_id(user_id)

        return OnboardingResponse(
            profile=ProfileResponse.model_validate(profile),
            message="Onboarding completed successfully! Your identity is locked for 30 days.",
        )

    async def get_archetypes(self) -> list:
        """Get all available archetypes."""
        return await self.profile_repo.get_all_archetypes()

    async def get_life_modes(self) -> list:
        """Get all available life modes."""
        return await self.profile_repo.get_all_life_modes()

    async def get_life_areas(self) -> list:
        """Get all available life areas."""
        return await self.profile_repo.get_all_life_areas()
