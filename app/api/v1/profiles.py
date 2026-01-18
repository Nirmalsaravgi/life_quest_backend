"""
Profiles API Endpoints

Handles user profile management and onboarding.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import (
    PlayerNameTakenError,
    ProfileNotFoundError,
    ValidationError,
)
from app.schemas.profile import (
    ArchetypeResponse,
    LifeAreaResponse,
    LifeModeResponse,
    OnboardingRequest,
    OnboardingResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


async def get_profile_service(db: DbSession) -> ProfileService:
    """Get a ProfileService instance."""
    return ProfileService(db)


ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get current user's profile",
)
async def get_my_profile(
    current_user: CurrentUser,
    profile_service: ProfileServiceDep,
) -> ProfileResponse:
    """
    Get the current user's game profile.
    
    Requires authentication. Returns 404 if profile not yet created.
    """
    try:
        profile = await profile_service.get_profile(current_user.id)
        return await profile_service.get_profile_response(profile)
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete onboarding first.",
        )


@router.patch(
    "/me",
    response_model=ProfileResponse,
    summary="Update current user's profile",
)
async def update_my_profile(
    data: ProfileUpdateRequest,
    current_user: CurrentUser,
    profile_service: ProfileServiceDep,
) -> ProfileResponse:
    """
    Update the current user's profile.
    
    Only avatar_url, bio, and timezone can be updated after onboarding.
    Player name can only be changed if identity is not locked.
    """
    try:
        profile = await profile_service.update_profile(current_user.id, data)
        return await profile_service.get_profile_response(profile)
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete onboarding first.",
        )
    except PlayerNameTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Complete onboarding",
)
async def complete_onboarding(
    data: OnboardingRequest,
    current_user: CurrentUser,
    profile_service: ProfileServiceDep,
) -> OnboardingResponse:
    """
    Complete the onboarding process.
    
    Creates user profile with:
    - **player_name**: Unique in-game name (3-50 chars)
    - **archetype_id**: Selected archetype (Explorer, Builder, etc.)
    - **life_mode_id**: Selected mode (Discipline, Growth, Recovery)
    - **life_area_ids**: 1-3 life areas to focus on
    
    Identity (archetype/mode) is locked for 30 days after onboarding.
    """
    try:
        return await profile_service.complete_onboarding(current_user.id, data)
    except PlayerNameTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    "/archetypes",
    response_model=list[ArchetypeResponse],
    summary="List all archetypes",
)
async def list_archetypes(
    profile_service: ProfileServiceDep,
) -> list[ArchetypeResponse]:
    """
    Get all available player archetypes.
    
    No authentication required.
    """
    archetypes = await profile_service.get_archetypes()
    return [ArchetypeResponse.model_validate(a) for a in archetypes]


@router.get(
    "/life-modes",
    response_model=list[LifeModeResponse],
    summary="List all life modes",
)
async def list_life_modes(
    profile_service: ProfileServiceDep,
) -> list[LifeModeResponse]:
    """
    Get all available life modes.
    
    No authentication required.
    """
    life_modes = await profile_service.get_life_modes()
    return [LifeModeResponse.model_validate(m) for m in life_modes]


@router.get(
    "/life-areas",
    response_model=list[LifeAreaResponse],
    summary="List all life areas",
)
async def list_life_areas(
    profile_service: ProfileServiceDep,
) -> list[LifeAreaResponse]:
    """
    Get all available life areas.
    
    No authentication required.
    """
    life_areas = await profile_service.get_life_areas()
    return [LifeAreaResponse.model_validate(a) for a in life_areas]
