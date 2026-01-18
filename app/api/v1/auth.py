"""
Authentication API Endpoints

Handles user registration, login, logout, and token refresh.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import AuthServiceDep, CurrentUser, get_client_info
from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: Request,
    data: RegisterRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """
    Register a new user with email and password.
    
    - **email**: Valid email address
    - **password**: Min 8 characters with at least 1 special character
    
    Returns access and refresh tokens.
    """
    client_info = get_client_info(request)
    
    try:
        return await auth_service.register(
            email=data.email,
            password=data.password,
            device_info=client_info["device_info"],
            ip_address=client_info["ip_address"],
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
async def login(
    request: Request,
    data: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """
    Authenticate user with email and password.
    
    Returns access and refresh tokens.
    """
    client_info = get_client_info(request)
    
    try:
        return await auth_service.login(
            email=data.email,
            password=data.password,
            device_info=client_info["device_info"],
            ip_address=client_info["ip_address"],
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """
    Get new tokens using a refresh token.
    
    - **refresh_token**: Valid refresh token from login/register
    
    Returns new access and refresh tokens.
    """
    client_info = get_client_info(request)
    
    try:
        return await auth_service.refresh_tokens(
            refresh_token=data.refresh_token,
            device_info=client_info["device_info"],
            ip_address=client_info["ip_address"],
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout current session",
)
async def logout(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Logout by invalidating the refresh token session.
    
    - **refresh_token**: The refresh token to invalidate
    """
    await auth_service.logout(session_token=data.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout from all devices",
)
async def logout_all(
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Logout from all devices by invalidating all sessions.
    
    Requires authentication.
    """
    await auth_service.logout_all(user_id=current_user.id)
    return MessageResponse(message="Successfully logged out from all devices")


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login with Google OAuth",
)
async def google_login(
    request: Request,
    data: GoogleAuthRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """
    Authenticate or register user with Google OAuth.
    
    - **id_token**: Google ID token from client-side authentication
    
    Returns access and refresh tokens.
    If user doesn't exist, creates a new account.
    """
    from app.core.oauth import GoogleOAuthError
    
    client_info = get_client_info(request)
    
    try:
        return await auth_service.google_login(
            id_token=data.id_token,
            device_info=client_info["device_info"],
            ip_address=client_info["ip_address"],
        )
    except GoogleOAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
