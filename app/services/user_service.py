"""
User Service

Business logic for user operations.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: UUID) -> User:
        """
        Get a user by ID.
        
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_response(self, user: User) -> UserResponse:
        """Convert user to response schema."""
        return UserResponse.model_validate(user)
