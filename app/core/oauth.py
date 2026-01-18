"""
Google OAuth Helper

Verifies Google ID tokens and extracts user information.
"""

from typing import Any

from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import settings
from app.core.exceptions import AuthenticationError


class GoogleOAuthError(AuthenticationError):
    """Raised when Google OAuth verification fails."""

    pass


async def verify_google_token(token: str) -> dict[str, Any]:
    """
    Verify a Google ID token and extract user info.
    
    Args:
        token: Google ID token from client
    
    Returns:
        Dict with user info: {email, sub, name, picture, given_name, family_name}
    
    Raises:
        GoogleOAuthError: If token is invalid or verification fails
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # Verify issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise GoogleOAuthError("Invalid token issuer")

        # Extract user info
        return {
            "email": idinfo.get("email"),
            "sub": idinfo.get("sub"),  # Google's unique user ID
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "given_name": idinfo.get("given_name"),
            "family_name": idinfo.get("family_name"),
            "email_verified": idinfo.get("email_verified", False),
            "locale": idinfo.get("locale"),
        }
    except ValueError as e:
        raise GoogleOAuthError(f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise GoogleOAuthError(f"Google OAuth verification failed: {str(e)}")
