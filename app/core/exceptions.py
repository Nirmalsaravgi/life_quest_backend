"""
Custom Exception Classes

Application-specific exceptions for consistent error handling.
"""

from typing import Any


class LifeQuestException(Exception):
    """Base exception for LifeQuest application."""

    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class AuthenticationError(LifeQuestException):
    """Raised when authentication fails."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class UserNotFoundError(LifeQuestException):
    """Raised when a user is not found."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class UserAlreadyExistsError(LifeQuestException):
    """Raised when trying to create a user that already exists."""

    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message)


class ProfileNotFoundError(LifeQuestException):
    """Raised when a user profile is not found."""

    def __init__(self, message: str = "Profile not found"):
        super().__init__(message)


class PlayerNameTakenError(LifeQuestException):
    """Raised when a player name is already taken."""

    def __init__(self, message: str = "This player name is already taken"):
        super().__init__(message)


class ValidationError(LifeQuestException):
    """Raised when validation fails."""

    pass


class PasswordValidationError(ValidationError):
    """Raised when password doesn't meet requirements."""

    pass


class NotFoundError(LifeQuestException):
    """Raised when a resource is not found."""

    pass


class PermissionDeniedError(LifeQuestException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)
