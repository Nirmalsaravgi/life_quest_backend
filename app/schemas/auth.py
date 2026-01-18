"""
Authentication Schemas

Pydantic models for auth request/response validation.
"""

from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import validate_password


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, v: str) -> str:
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Google OAuth login request."""

    id_token: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
