"""
Provides the custom, scope-based permission classes for the RBAC system.
"""

from typing import Dict
from typing import List

from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class HasScope(BasePermission):
    """
    A custom DRF permission class that checks for RBAC scopes.

    This permission relies on the `RBACMiddleware`, which must be installed.
    The middleware pre-calculates the user's permissions and attaches them
    to the request as `request.user.scopes`. This class then checks that
    pre-calculated dictionary, making permission checks extremely fast as they
    do not require any database queries.

    A view using this permission must define a `required_scope` attribute.

    Attributes:
        message (str): The error message to return on failure.
        required_scope (str): The scope required for access, in the format
                              "resource:action" (e.g., "projects:read"). This
                              must be set on the view.
    """

    message = "You do not have the required permission to perform this action."

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Checks if the user has the required scope to access the view.

        Returns:
            True if the user has permission, False otherwise.
        """
        # Superusers and staff have all permissions implicitly.
        if (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        ):
            return True

        # The view must define the scope it requires.
        required_scope: str = getattr(view, "required_scope", None)
        if not required_scope:
            # For safety, deny access if the view is not configured.
            return False

        # The user must be authenticated to have scopes.
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the scopes dictionary attached by the middleware.
        user_scopes: Dict[str, List[str]] = getattr(request.user, "scopes", {})

        # Split "resource:action" into its parts.
        try:
            resource, action = required_scope.split(":")
        except ValueError:
            # Handle cases where required_scope is malformed.
            return False

        # Check if the user's scopes grant the required permission.
        return action in user_scopes.get(resource, [])
