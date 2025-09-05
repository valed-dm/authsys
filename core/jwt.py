"""
A centralized module for JWT (JSON Web Token) creation and validation.

This module encapsulates all logic related to the JWT lifecycle, providing
strongly-typed, secure functions for generating and decoding tokens. It acts
as the cryptographic core for the application's token-based authentication.
"""

import time
from typing import Tuple
from typing import cast

from django.conf import settings
import jwt
from typing_extensions import TypedDict


# --- Type Definition for our JWT Payload ---
class JWTPayload(TypedDict):
    """
    Defines the precise structure of the JWT payload for static analysis.
    """

    sub: int  # Subject (the user's ID)
    type: str  # Custom claim ('access' or 'refresh')
    iat: int  # Issued At (timestamp)
    exp: int  # Expiration (timestamp)


# --- JWT Configuration ---
ACCESS_TOKEN_LIFETIME_SECONDS: int = getattr(settings, "JWT_ACCESS_TTL", 3600)
REFRESH_TOKEN_LIFETIME_SECONDS: int = getattr(settings, "JWT_REFRESH_TTL", 86400)
JWT_SECRET_KEY: str = settings.JWT_SECRET
JWT_ALGORITHM: str = settings.JWT_ALG


def generate_tokens(user_id: int) -> Tuple[str, str]:
    """
    Generates a pair of JWTs: an access token and a refresh token.

    This function creates stateless tokens conforming to the JWTPayload structure.

    Args:
        user_id: The primary key of the user for whom to generate tokens.
                 This will be encoded in the 'sub' (subject) claim.

    Returns:
        A tuple containing the encoded access token and refresh token as strings.
        (access_token, refresh_token)
    """
    now = int(time.time())

    access_payload: JWTPayload = {
        "sub": user_id,
        "type": "access",
        "iat": now,
        "exp": now + ACCESS_TOKEN_LIFETIME_SECONDS,
    }
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    refresh_payload: JWTPayload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + REFRESH_TOKEN_LIFETIME_SECONDS,
    }
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token


def decode_token(token: str) -> JWTPayload:
    """
    Decodes and validates a JWT, returning its strongly-typed payload.

    Wraps the `pyjwt` library's decode method, automatically verifying the
    token's signature and expiration.

    Args:
        token: The encoded JWT string to be decoded.

    Returns:
        A JWTPayload dictionary containing the token's claims.

    Raises:
        jwt.PyJWTError: If the token is invalid, expired, or has a bad
            signature.
        AssertionError: If the decoded payload is not a dictionary.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    # Ensure the payload is a dictionary, which is expected for our JWTPayload.
    assert isinstance(payload, dict)

    # Cast the validated dictionary to specific TypedDict for static analysis.
    return cast(JWTPayload, payload)
