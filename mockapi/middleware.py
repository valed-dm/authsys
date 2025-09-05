"""
Provides a mock middleware for development and testing purposes.

This middleware simulates the behavior of the real `RBACMiddleware` by attaching
a predefined set of permission scopes to authenticated users.
"""

from typing import Callable
from typing import Dict
from typing import List

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.http import HttpResponse


User = get_user_model()


class MockScopesMiddleware:
    """
    Attaches a hardcoded dictionary of permission scopes to authenticated users.

    This middleware is intended for **development or testing only**. It allows
    views protected by the `HasScope` permission class to function without
    requiring a fully configured RBAC database.

    It should be placed **before** the real `RBACMiddleware` in the settings
    so that it can attach the scopes first. If the `scopes` attribute already
    exists (e.g., attached by the real middleware), this will do nothing.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initializes the middleware instance."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        The main logic of the middleware, executed on each request.
        """
        user: User = request.user

        # We only operate on authenticated users.
        if hasattr(request, "user") and user.is_authenticated:
            # Check if scopes have NOT already been attached by another middleware.
            if not hasattr(user, "scopes"):
                mock_scopes: Dict[str, List[str]] = {}
                if user.is_superuser:
                    # Grant superusers a powerful set of mock permissions.
                    mock_scopes = {
                        "projects": ["read", "create", "delete"],
                        "invoices": ["read", "create", "delete"],
                    }
                else:
                    # Grant regular users a limited, read-only set.
                    mock_scopes = {
                        "projects": ["read"],
                        "invoices": ["read"],
                    }
                user.scopes = mock_scopes

        response = self.get_response(request)
        return response
