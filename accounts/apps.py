import os

from django.apps import AppConfig

from authsys.settings import log


class AccountsConfig(AppConfig):
    """
    Application configuration for the 'accounts' app.

    This class is the entry point for app-specific initialization,
    such as connecting signals or setting up admin configurations
    when the Django application starts.
    """

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "accounts"

    def ready(self) -> None:
        """
        Executes startup logic when the app is ready.

        This method is called by Django during the application loading process.
        It is the ideal place for one-time initialization tasks.

        Here, we connect the `manage_user_roles` signal to the User model's
        `post_save` event and override the default Django admin login form.

        The `RUN_MAIN` check prevents this logic from running twice in the
        development server's autoreload process.
        """
        if os.environ.get("RUN_MAIN") != "true":
            return

        # --- Signal Connection ---
        # Import signals locally to avoid circular import issues at startup.
        from django.conf import settings
        from django.db.models.signals import post_save

        from . import signals

        # Connect the function to the signal.
        # This ensures user roles are managed automatically on user creation/update.
        post_save.connect(
            signals.manage_user_roles,
            sender=settings.AUTH_USER_MODEL,
            dispatch_uid="accounts.signals.manage_user_roles",
        )

        # --- Admin Customization ---
        from django.contrib import admin

        from .forms import EmailAdminAuthenticationForm

        # Override the default Django admin login form with custom email-based form.
        admin.site.login_form = EmailAdminAuthenticationForm

        log.info(
            "✅ Accounts app is ready: Custom admin form and signals connected."
        )
