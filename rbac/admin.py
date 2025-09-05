"""
Admin interface configuration for the Role-Based Access Control (RBAC) app.

This file registers the RBAC models with the Django admin site and customizes
their appearance and functionality to create an intuitive management interface.
"""

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Action
from .models import Permission
from .models import Resource
from .models import Role
from .models import RolePermission


# --- Inlines ---


class RolePermissionInline(admin.TabularInline):
    """
    An inline editor for the Role-Permission relationship.

    This is the key to a good user experience. It allows an administrator to
    add, edit, and remove permissions directly on the detail page of a Role,
    rather than managing the "through" model in a separate interface.
    """

    model = RolePermission
    extra = 1  # Provides one empty slot for adding a new permission.
    autocomplete_fields = ["permission"]  # Enables a search-as-you-type widget.
    verbose_name = "Assigned Permission"
    verbose_name_plural = "Assigned Permissions"


# --- ModelAdmins ---


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for the Role model."""

    list_display = ("name", "description")
    search_fields = ("name",)

    # By including the inline, the Role change page becomes the central
    # hub for managing which permissions are associated with a role.
    inlines = [RolePermissionInline]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for the Permission model."""

    list_display = ("__str__", "resource", "action")
    list_filter = ("resource", "action")

    # Defining search_fields is crucial for enabling the `autocomplete_fields`
    # in the RolePermissionInline to work efficiently.
    search_fields = ("resource__code", "action__code")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimizes the changelist query by prefetching related models."""
        return super().get_queryset(request).select_related("resource", "action")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin interface for the Resource model."""

    list_display = ("code", "description")
    search_fields = ("code",)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """Admin interface for the Action model."""

    list_display = ("code", "description")
    search_fields = ("code",)
