from typing import Any
from typing import Type

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from rbac.models import Role
from rbac.models import UserRole


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_roles(
    sender: Type[User],
    instance: User,
    created, **kwargs: Any,
) -> None:
    """
    Automates RBAC role assignments when a User is created or updated.

    This signal handler is connected to the `post_save` event for the User model
    and enforces the following business rules:

    1.  **On User Creation (`created` is True):**
        - If the new user is a superuser, they automatically get the 'Admin' role.
        - If the new user is a regular user, they get the 'Default' role.

    2.  **On User Update (`created` is False):**
        - If an existing user is promoted to be a superuser, this signal ensures
          they are also granted the 'Admin' role.

    This keeps Django's built-in auth system in sync with the custom RBAC system.

    The `get_or_create` method is used to robustly find or create the necessary
    roles, making this logic safe to run in any environment.
    """

    if created:
        # --- Handle NEW users ---
        if instance.is_superuser:
            # If a superuser is created, give them the Admin role.
            admin_role, _ = Role.objects.get_or_create(
                name="Admin",
                defaults={"description": "Full system access for administrators."},
            )
            UserRole.objects.get_or_create(user=instance, role=admin_role)
        else:
            # If a regular user is created, give them the Default role.
            default_role, _ = Role.objects.get_or_create(
                name="Default",
                defaults={"description": "Default permissions for new users."},
            )
            UserRole.objects.get_or_create(user=instance, role=default_role)

    elif instance.is_superuser:
        # --- Handle UPDATED users ---
        # If an existing user is promoted to superuser, ensure they get the Admin role.
        admin_role, _ = Role.objects.get_or_create(name="Admin")
        UserRole.objects.get_or_create(user=instance, role=admin_role)
