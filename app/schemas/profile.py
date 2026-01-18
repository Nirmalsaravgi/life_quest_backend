"""
Profile Schemas

Pydantic models for user profile request/response.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ArchetypeResponse(BaseModel):
    """Archetype response."""

    id: UUID
    name: str
    description: str | None
    passive_bonuses: dict | None

    model_config = {"from_attributes": True}


class LifeModeResponse(BaseModel):
    """Life mode response."""

    id: UUID
    name: str
    description: str | None
    modifiers: dict | None

    model_config = {"from_attributes": True}


class LifeAreaResponse(BaseModel):
    """Life area response."""

    id: UUID
    name: str
    emoji: str | None
    description: str | None

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    """User profile response."""

    id: UUID
    user_id: UUID
    player_name: str
    level: int
    total_core_xp: int
    avatar_url: str | None
    bio: str | None
    timezone: str
    onboarding_completed: bool
    identity_locked_until: datetime | None
    archetype: ArchetypeResponse | None
    life_mode: LifeModeResponse | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileCreateRequest(BaseModel):
    """Profile creation during onboarding."""

    player_name: str = Field(..., min_length=3, max_length=50)
    archetype_id: UUID
    life_mode_id: UUID
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    timezone: str = "UTC"


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""

    player_name: str | None = Field(None, min_length=3, max_length=50)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    timezone: str | None = None


class LifeAreaSelectionRequest(BaseModel):
    """Request to select life areas (max 3)."""

    life_area_ids: list[UUID] = Field(..., min_length=1, max_length=3)


class OnboardingRequest(BaseModel):
    """Complete onboarding request."""

    player_name: str = Field(..., min_length=3, max_length=50)
    archetype_id: UUID
    life_mode_id: UUID
    life_area_ids: list[UUID] = Field(..., min_length=1, max_length=3)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    timezone: str = "UTC"


class OnboardingResponse(BaseModel):
    """Onboarding completion response."""

    profile: ProfileResponse
    message: str = "Onboarding completed successfully"
