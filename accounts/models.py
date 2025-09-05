from typing import Any
from typing import Optional

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Provides helper methods to create regular users and superusers,
    ensuring email is normalized and passwords are properly hashed.
    """

    def create_user(
        self, email: str, password: Optional[str] = None, **extra_fields: Any
    ) -> "User":
        """
        Creates and saves a new regular User with an email and password.

        Args:
            email: The user's email address. Will be normalized.
            password: The user's raw password. Will be hashed.
            **extra_fields: Additional fields for the user model.

        Returns:
            The newly created User instance.

        Raises:
            ValueError: If the email field is not provided.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: Optional[str] = None, **extra_fields: Any
    ) -> "User":
        """
        Creates and saves a new superuser with enforced staff and superuser status.

        Args:
            email: The superuser's email address.
            password: The superuser's raw password.
            **extra_fields: Additional fields for the user model.

        Returns:
            The newly created superuser instance.

        Raises:
            ValueError: If `is_staff` or `is_superuser` is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the application.

    Uses email as the unique identifier for authentication instead of a username.
    Includes fields for personal information, staff/superuser status, and a
    soft-delete mechanism.
    """

    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_("Required. The primary means of user identification and login."),
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # --- Soft-delete fields ---
    is_deleted = models.BooleanField(
        _("is deleted"),
        default=False,
        help_text=_("Designates whether this user has been soft-deleted."),
    )
    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
        help_text=_("The timestamp when the user was soft-deleted."),
    )

    # --- Configuration ---
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """Returns the email address as the string representation of the user."""
        return self.email

    # --- Custom Methods ---
    def soft_delete(self) -> None:
        """

        Performs a soft delete on the user.

        Sets the `is_deleted` flag to True, deactivates the user, and records
        the deletion timestamp. The user object is not removed from the database.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])

    def restore(self) -> None:
        """
        Restores a soft-deleted user.

        Resets the `is_deleted` flag, clears the deletion timestamp, and
        reactivates the user account.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])
