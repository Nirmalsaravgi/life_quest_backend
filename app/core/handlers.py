"""
Global Exception Handlers

FastAPI exception handlers for consistent error responses.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    LifeQuestException,
    NotFoundError,
    PermissionDeniedError,
    PlayerNameTakenError,
    ProfileNotFoundError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError as AppValidationError,
)

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "error",
    details: Any = None,
) -> JSONResponse:
    """Create a consistent error response."""
    content = {
        "error": {
            "type": error_type,
            "message": message,
        }
    }
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors from request body/params."""
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            errors.append({
                "field": loc,
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(f"Validation error: {errors}")
        
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_type="validation_error",
            details=errors,
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        """Handle invalid login credentials."""
        return create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=exc.message,
            error_type="invalid_credentials",
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(
        request: Request, exc: InvalidTokenError
    ) -> JSONResponse:
        """Handle invalid JWT tokens."""
        return create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=exc.message,
            error_type="invalid_token",
        )

    @app.exception_handler(TokenExpiredError)
    async def token_expired_handler(
        request: Request, exc: TokenExpiredError
    ) -> JSONResponse:
        """Handle expired tokens."""
        return create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=exc.message,
            error_type="token_expired",
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        """Handle general authentication errors."""
        return create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=exc.message,
            error_type="authentication_error",
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        """Handle user not found errors."""
        return create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=exc.message,
            error_type="user_not_found",
        )

    @app.exception_handler(ProfileNotFoundError)
    async def profile_not_found_handler(
        request: Request, exc: ProfileNotFoundError
    ) -> JSONResponse:
        """Handle profile not found errors."""
        return create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=exc.message,
            error_type="profile_not_found",
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Handle generic not found errors."""
        return create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=exc.message,
            error_type="not_found",
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        """Handle duplicate user registration."""
        return create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            message=exc.message,
            error_type="user_already_exists",
        )

    @app.exception_handler(PlayerNameTakenError)
    async def player_name_taken_handler(
        request: Request, exc: PlayerNameTakenError
    ) -> JSONResponse:
        """Handle duplicate player name."""
        return create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            message=exc.message,
            error_type="player_name_taken",
        )

    @app.exception_handler(AppValidationError)
    async def app_validation_handler(
        request: Request, exc: AppValidationError
    ) -> JSONResponse:
        """Handle application-level validation errors."""
        return create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=exc.message,
            error_type="validation_error",
            details=exc.details,
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(
        request: Request, exc: PermissionDeniedError
    ) -> JSONResponse:
        """Handle permission denied errors."""
        return create_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            message=exc.message,
            error_type="permission_denied",
        )

    @app.exception_handler(LifeQuestException)
    async def lifequest_exception_handler(
        request: Request, exc: LifeQuestException
    ) -> JSONResponse:
        """Handle any other LifeQuest exceptions."""
        logger.error(f"LifeQuest exception: {exc.message}", exc_info=True)
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exc.message,
            error_type="application_error",
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(f"Unexpected error: {str(exc)}")
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            error_type="internal_error",
        )
