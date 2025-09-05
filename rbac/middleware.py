"""
Provides middleware for the Role-Based Access Control (RBAC) system.
"""

from typing import Callable
from typing import Dict
from typing import List

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.http import HttpResponse

from .models import UserRole


User = get_user_model()


class RBACMiddleware:
    """

    A middleware that pre-calculates and attaches a user's permissions to the request.

    On every authenticated request, this middleware performs an efficient,
    pre-optimized database query to fetch all permissions associated with the
    current user's roles.

    It then constructs a `scopes` dictionary and attaches it to `request.user`.
    This allows the `HasScope` permission class to perform extremely fast,
    in-memory checks without hitting the database on every permission validation.

    The format of the attached `scopes` dictionary is:
    `{"resource_code": ["action_code", "another_action_code", ...]}`
    Example: `{"projects": ["read", "create"], "invoices": ["read"]}`
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initializes the middleware instance."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        The main logic of the middleware, executed on each request.
        """
        user: User = request.user

        if user.is_authenticated:
            # This is a highly optimized query. `prefetch_related` fetches all
            # related data for all the user's roles in just a few queries,
            # preventing the "N+1" problem.
            user_roles = UserRole.objects.filter(user=user).prefetch_related(
                "role__role_perms__permission__resource",
                "role__role_perms__permission__action",
            )

            scopes: Dict[str, List[str]] = {}
            for user_role in user_roles:
                # The prefetched data is now available in memory.
                for role_perm in user_role.role.role_perms.all():
                    permission = role_perm.permission
                    resource_code = permission.resource.code
                    action_code = permission.action.code

                    # Use setdefault to initialize the list if the resource key is new.
                    scopes.setdefault(resource_code, []).append(action_code)

            # Attach the calculated scopes to the user object for this request.
            user.scopes = scopes
        else:
            # Ensure anonymous users always have an empty scopes dictionary.
            user.scopes = {}

        response = self.get_response(request)
        return response
