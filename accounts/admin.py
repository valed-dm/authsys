from typing import Any
from typing import List
from typing import Tuple

from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from rbac.models import UserRole


User = get_user_model()


class UserRoleInline(admin.TabularInline):
    """
    Inline admin view for managing a user's roles directly on the User change page.

    Provides an intuitive way for administrators to see and assign roles
    to a specific user without navigating to a separate interface.
    """

    model = UserRole
    extra = 1
    autocomplete_fields = ["role"]
    verbose_name = "Role Assignment"
    verbose_name_plural = "Role Assignments"


class DeletionStatusFilter(admin.SimpleListFilter):
    """
    Custom admin filter to view users based on their soft-deleted status.

    This provides a clear "Deleted" / "Active" choice in the admin filter sidebar,
    which is more intuitive than the default boolean filter.
    """

    title = _("deletion status")
    parameter_name = "deleted"

    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        """Returns the filter's display options."""
        return [
            ("yes", _("Deleted")),
            ("no", _("Active")),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        """Applies the filter to the user list queryset."""
        if self.value() == "yes":
            return queryset.filter(is_deleted=True)
        if self.value() == "no":
            return queryset.filter(is_deleted=False)
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the custom User model.

    Extends the base `UserAdmin` to include custom actions for soft-deletion,
    a restore mechanism, and inline management of RBAC roles.
    """

    # Configuration
    inlines = [UserRoleInline]
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_deleted",
        "restore_button",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        DeletionStatusFilter,
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    actions = ["soft_delete_selected"]

    # Fieldset configuration, hiding non-editable fields
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Soft Delete"), {"fields": ("is_deleted", "deleted_at")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined", "deleted_at")

    # --- Custom Actions & Methods ---

    @admin.action(description=_("Soft delete selected users"))
    def soft_delete_selected(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Admin action to soft-delete multiple users from the changelist."""
        updated_count = queryset.update(is_deleted=True, is_active=False)
        self.message_user(
            request,
            _("Successfully soft-deleted %(count)d users.") % {"count": updated_count},
            messages.SUCCESS,
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Overrides the default queryset to show all users, including soft-deleted ones.

        This is crucial for allowing admins to find and restore deleted accounts.
        """
        # The base manager `objects` will show all users including deleted users.
        return User.objects.all()

    def restore_button(self, obj: User) -> str:
        """Displays a 'Restore' button in the changelist for soft-deleted users."""
        if obj.is_deleted:
            url = reverse("admin:accounts_user_restore", args=[obj.pk])
            return format_html('<a class="button" href="{}">Restore</a>', url)
        return "—"  # Render a dash for active users

    restore_button.short_description = _("Restore")
    restore_button.allow_tags = True

    def get_urls(self) -> List[path]:
        """Adds the custom 'restore' URL to the admin's URL patterns."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "restore/<int:pk>/",
                self.admin_site.admin_view(self.restore_user),
                name="accounts_user_restore",
            ),
        ]
        return custom_urls + urls

    def restore_user(self, request: HttpRequest, pk: int) -> HttpResponse:
        """View logic to handle the user restore action."""
        try:
            user = self.get_queryset(request).get(pk=pk, is_deleted=True)
            user.restore()
            self.message_user(
                request,
                f"User {user.email} was restored successfully.",
                messages.SUCCESS,
            )
        except User.DoesNotExist:
            self.message_user(
                request, "User not found or is not deleted.", messages.ERROR
            )

        # Redirect back to the user changelist page
        return redirect("admin:accounts_user_changelist")
