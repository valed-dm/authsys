"""
Application configuration for the 'rbac' (Role-Based Access Control) app.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RbacConfig(AppConfig):
    """
    Primary configuration for the RBAC application.

    This class allows Django to discover the app and its models. It also
    sets a human-readable `verbose_name`, which is used in the Django
    admin interface to provide a more descriptive title for the app section.
    """

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "rbac"
    verbose_name: str = _("Role-Based Access Control")
