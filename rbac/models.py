"""
Defines the database models for the Role-Based Access Control (RBAC) system.

This schema provides a flexible and granular way to manage user permissions.
The core idea is to define atomic Permissions (a Resource + an Action),
bundle them into Roles, and then assign those Roles to Users.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# --- Foundational RBAC Components ---


class Resource(models.Model):
    """
    Represents a "noun" or a component of the system that can be protected.

    Examples: "projects", "invoices", "users".
    """

    code = models.CharField(
        _("code"),
        max_length=100,
        unique=True,
        help_text=_(
            "A unique, machine-readable code for the resource (e.g., 'projects')."
        ),
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")
        ordering = ["code"]  # Order alphabetically for easier admin navigation

    def __str__(self) -> str:
        return self.code


class Action(models.Model):
    """

    Represents a "verb" or an operation that can be performed on a Resource.

    Examples: "create", "read", "update", "delete".
    """

    code = models.CharField(
        _("code"),
        max_length=100,
        unique=True,
        help_text=_("A unique, machine-readable code for the action (e.g., 'read')."),
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("action")
        verbose_name_plural = _("actions")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class Permission(models.Model):
    """

    An atomic rule that grants a specific Action on a specific Resource.

    This is the fundamental unit of authorization in the system.
    Example: The permission to "read" "projects" (`projects:read`).
    """

    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, verbose_name=_("resource")
    )
    action = models.ForeignKey(
        Action, on_delete=models.CASCADE, verbose_name=_("action")
    )

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        # Ensures that you cannot have a duplicate "projects:read" permission.
        unique_together = ("resource", "action")
        ordering = ["resource__code", "action__code"]

    def __str__(self) -> str:
        """Returns the permission in the standard 'resource:action' format."""
        return f"{self.resource.code}:{self.action.code}"


# --- Relational / "Through" Models ---


class Role(models.Model):
    """

    A named collection of Permissions that can be assigned to a user.

    A Role represents a job function or a level of access.
    Examples: "Admin", "Project Manager", "Viewer".
    """

    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("A unique, human-readable name for the role."),
    )
    description = models.TextField(_("description"), blank=True)
    # Permissions are linked via the RolePermission 'through' model.
    permissions = models.ManyToManyField(
        Permission, through="RolePermission", verbose_name=_("permissions"), blank=True
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RolePermission(models.Model):
    """

    The "through" model that links a Role to a Permission.

    This creates the many-to-many relationship between Roles and Permissions.
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_perms")
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="perm_roles"
    )

    class Meta:
        verbose_name = _("role permission")
        verbose_name_plural = _("role permissions")
        unique_together = ("role", "permission")


class UserRole(models.Model):
    """
    The "through" model that links a User to a Role.

    This creates the many-to-many relationship between Users and Roles.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")

    class Meta:
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")
        unique_together = ("user", "role")
