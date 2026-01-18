"""
Authentication Service

Business logic for user authentication, registration, and OAuth.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(
        self,
        email: str,
        password: str,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """
        Register a new user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password (already validated by schema)
            device_info: Optional device information
            ip_address: Optional IP address
        
        Returns:
            TokenResponse with access and refresh tokens
        
        Raises:
            UserAlreadyExistsError: If email is already registered
        """
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()

        # Create user
        password_hash = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            password_hash=password_hash,
            email_verified=False,  # Email verification not required per design
        )

        # Generate tokens
        tokens = await self._create_tokens_and_session(
            user=user,
            device_info=device_info,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            is_new_user=True,
        )

    async def login(
        self,
        email: str,
        password: str,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            device_info: Optional device information
            ip_address: Optional IP address
        
        Returns:
            TokenResponse with access and refresh tokens
        
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Verify password
        if not user.password_hash or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsError("Account is deactivated")

        # Update last login
        await self.user_repo.update_last_login(user)

        # Generate tokens
        tokens = await self._create_tokens_and_session(
            user=user,
            device_info=device_info,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            is_new_user=False,
        )

    async def refresh_tokens(
        self,
        refresh_token: str,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """
        Refresh access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            device_info: Optional device information
            ip_address: Optional IP address
        
        Returns:
            TokenResponse with new access and refresh tokens
        
        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        # Decode and validate token
        payload = decode_token(refresh_token)
        if not payload:
            raise InvalidTokenError()

        # Check token type
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise InvalidTokenError()

        # Generate new tokens
        tokens = await self._create_tokens_and_session(
            user=user,
            device_info=device_info,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            is_new_user=False,
        )

    async def logout(self, session_token: str) -> None:
        """
        Logout user by invalidating session.
        
        Args:
            session_token: The session token to invalidate
        """
        session = await self.user_repo.get_session_by_token(session_token)
        if session:
            await self.user_repo.delete_session(session)

    async def logout_all(self, user_id: UUID) -> None:
        """
        Logout user from all devices.
        
        Args:
            user_id: The user's ID
        """
        await self.user_repo.delete_all_user_sessions(user_id)

    async def get_current_user(self, token: str) -> User:
        """
        Get the current user from an access token.
        
        Args:
            token: JWT access token
        
        Returns:
            User object
        
        Raises:
            InvalidTokenError: If token is invalid
            UserNotFoundError: If user doesn't exist
        """
        payload = decode_token(token)
        if not payload:
            raise InvalidTokenError()

        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise InvalidTokenError("Account is deactivated")

        return user

    async def google_login(
        self,
        id_token: str,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """
        Authenticate or register user with Google OAuth.
        
        Args:
            id_token: Google ID token from client
            device_info: Optional device information
            ip_address: Optional IP address
        
        Returns:
            TokenResponse with access and refresh tokens
        
        Raises:
            AuthenticationError: If Google token is invalid
        """
        from app.core.oauth import verify_google_token

        # Verify Google token
        google_user = await verify_google_token(id_token)
        
        email = google_user.get("email")
        google_user_id = google_user.get("sub")
        
        if not email or not google_user_id:
            raise InvalidCredentialsError("Invalid Google token: missing email or user ID")

        is_new_user = False

        # Check if user exists
        user = await self.user_repo.get_by_email(email)
        
        if user:
            # User exists - update/create auth provider
            auth_provider = await self.user_repo.get_auth_provider(
                provider="google",
                provider_user_id=google_user_id,
            )
            
            if not auth_provider:
                # Link Google account to existing user
                await self.user_repo.create_auth_provider(
                    user_id=user.id,
                    provider="google",
                    provider_user_id=google_user_id,
                    provider_data={
                        "picture": google_user.get("picture"),
                        "given_name": google_user.get("given_name"),
                        "family_name": google_user.get("family_name"),
                        "locale": google_user.get("locale"),
                    },
                )
        else:
            # New user - create account
            is_new_user = True
            user = await self.user_repo.create(
                email=email,
                password_hash=None,  # OAuth-only user
                email_verified=google_user.get("email_verified", False),
            )
            
            # Create auth provider
            await self.user_repo.create_auth_provider(
                user_id=user.id,
                provider="google",
                provider_user_id=google_user_id,
                provider_data={
                    "picture": google_user.get("picture"),
                    "given_name": google_user.get("given_name"),
                    "family_name": google_user.get("family_name"),
                    "locale": google_user.get("locale"),
                },
            )

        # Update last login
        await self.user_repo.update_last_login(user)

        # Generate tokens
        tokens = await self._create_tokens_and_session(
            user=user,
            device_info=device_info,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            is_new_user=is_new_user,
        )

    async def _create_tokens_and_session(
        self,
        user: User,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> dict[str, str]:
        """Create access token, refresh token, and session."""
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        # Create session for refresh token tracking
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.user_repo.create_session(
            user_id=user.id,
            session_token=refresh_token,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
