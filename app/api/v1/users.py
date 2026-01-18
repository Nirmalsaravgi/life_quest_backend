"""
Users API Endpoints

Handles user-related operations.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get the currently authenticated user's information.
    
    Requires authentication.
    """
    return UserResponse.model_validate(current_user)
