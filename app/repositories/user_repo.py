"""
User Repository

Data access layer for user-related database operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import AuthProvider, User, UserSession


class UserRepository:
    """Repository for User, AuthProvider, and UserSession operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== User Operations ====================

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str | None = None,
        email_verified: bool = False,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            email_verified=email_verified,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

    # ==================== Auth Provider Operations ====================

    async def get_auth_provider(
        self, provider: str, provider_user_id: str
    ) -> AuthProvider | None:
        """Get an auth provider by provider name and user ID."""
        result = await self.db.execute(
            select(AuthProvider).where(
                AuthProvider.provider == provider,
                AuthProvider.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_auth_provider(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expires_at: datetime | None = None,
        provider_data: dict | None = None,
    ) -> AuthProvider:
        """Create a new auth provider connection."""
        auth_provider = AuthProvider(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            provider_data=provider_data,
        )
        self.db.add(auth_provider)
        await self.db.flush()
        return auth_provider

    async def update_auth_provider_tokens(
        self,
        auth_provider: AuthProvider,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expires_at: datetime | None = None,
    ) -> None:
        """Update OAuth tokens for an auth provider."""
        if access_token is not None:
            auth_provider.access_token = access_token
        if refresh_token is not None:
            auth_provider.refresh_token = refresh_token
        if token_expires_at is not None:
            auth_provider.token_expires_at = token_expires_at
        await self.db.flush()

    # ==================== Session Operations ====================

    async def create_session(
        self,
        user_id: UUID,
        session_token: str,
        expires_at: datetime,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> UserSession:
        """Create a new user session."""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_session_by_token(self, session_token: str) -> UserSession | None:
        """Get a session by its token."""
        result = await self.db.execute(
            select(UserSession).where(UserSession.session_token == session_token)
        )
        return result.scalar_one_or_none()

    async def delete_session(self, session: UserSession) -> None:
        """Delete a user session."""
        await self.db.delete(session)
        await self.db.flush()

    async def delete_all_user_sessions(self, user_id: UUID) -> None:
        """Delete all sessions for a user."""
        result = await self.db.execute(
            select(UserSession).where(UserSession.user_id == user_id)
        )
        sessions = result.scalars().all()
        for session in sessions:
            await self.db.delete(session)
        await self.db.flush()
