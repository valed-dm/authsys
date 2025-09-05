from typing import Any
from typing import Dict

from django.http import HttpRequest
from django.views.generic.base import ContextMixin


# By inheriting from ContextMixin, we ensure that the get_context_data
# method signature is compatible with Django's generic views.
class JWTContextMixin(ContextMixin):
    """
    A Django view mixin to inject JWTs from the session into the template context.

    This mixin is designed to be used with Django's class-based views
    (e.g., TemplateView, ListView, or any view that renders a template). It
    retrieves the 'access_token' and 'refresh_token' that were stored in the
    user's session during login and makes them available in the template.

    This is useful for passing tokens to frontend JavaScript for making
    authenticated API calls.

    Attributes:
        request (HttpRequest): The current request object, automatically
            attached to the view instance by Django's dispatcher.
    """

    request: HttpRequest

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds JWT access and refresh tokens to the template context.

        It safely retrieves tokens from the session, providing an empty
        string if a token is not found.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the context.

        Returns:
            A dictionary representing the template context, updated with
            the JWTs.
        """

        # The `super().get_context_data(**kwargs)` call ensures that we
        # respect and include any context data provided by other parent
        # classes in the inheritance chain (like ListView's object_list).
        context = super().get_context_data(**kwargs)

        # Add our custom context data.
        context["jwt_access_token"] = self.request.session.get("access_token", "")
        context["jwt_refresh_token"] = self.request.session.get("refresh_token", "")

        return context
