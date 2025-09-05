from typing import Optional
from typing import Tuple

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from core.jwt import JWTPayload
from core.jwt import decode_token


User = get_user_model()


class BearerJWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication backend for Django REST Framework.

    This backend authenticates requests containing a JWT in the `Authorization`
    header with the "Bearer" scheme. It validates the token's signature,
    expiration, and type, then retrieves the active user associated with it.

    This class is designed to be the primary authentication method for the API.
    """

    keyword: str = "Bearer"

    def authenticate(self, request: HttpRequest) -> Optional[Tuple[User, None]]:
        """
        Authenticates the incoming request based on a Bearer JWT.

        Args:
            request: The incoming HttpRequest object.

        Returns:
            A tuple of (user, None) if authentication is successful.
            `None` if no 'Authorization' header is found or the scheme is incorrect.

        Raises:
            AuthenticationFailed: If the token is invalid, expired, of the wrong
                type, or if the associated user is not found, inactive, or deleted.
        """
        # 1. Extract the token from the 'Authorization' header.
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            # If the header is missing or doesn't use the Bearer scheme,
            # this backend does not apply. Return None to allow other
            # authentication methods to be tried.
            return None

        token = auth_header.split(" ", 1)[1].strip()

        # 2. Decode and validate the JWT.
        try:
            payload: JWTPayload = decode_token(token)
        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid or expired token") from e

        # 3. Verify that the token is an 'access' token.
        if payload["type"] != "access":
            raise exceptions.AuthenticationFailed(
                "Invalid token type provided; expected 'access'."
            )

        # 4. Retrieve the user from the database.
        user_id = payload["sub"]
        if not user_id:
            raise exceptions.AuthenticationFailed(
                "Token is missing user identifier (sub)."
            )

        try:
            # Ensure the user exists, is active, and has not been soft-deleted.
            # This is a critical security check.
            user = User.objects.get(id=user_id, is_active=True, is_deleted=False)
        except User.DoesNotExist as e:
            raise exceptions.AuthenticationFailed(
                "User not found, inactive, or deleted."
            ) from e

        # 5. Success.
        return user, None
