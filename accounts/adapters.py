from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from .services import register_user


User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapts the django-allauth user creation process.

    Intercepts the `save_user` hook to delegate the actual user creation
    to the application's centralized `register_user` service function.
    """

    def save_user(
        self, request: HttpRequest, user: User, form: forms.Form, commit: bool = True
    ) -> User:
        """
        Saves a new user account.

        This override ignores the partially created `user` object from allauth
        and instead uses the form's cleaned data to call the robust, atomic
        `register_user` service.

        Args:
            request: The current HTTP request.
            user: An unsaved user instance created by allauth.
            form: The signup form containing the cleaned data.
            commit: (Ignored) The service function always commits.

        Returns:
            The newly created and saved user instance.
        """
        # We extract only the data we need, ignoring the `commit` flag
        # as our service layer handles the transaction.
        data: dict[str, Any] = form.cleaned_data
        password: str = data.get("password")  # Allauth uses `password` from the form
        email: str = data.get("email")

        # Delegate to the centralized service for user creation.
        user = register_user(email=email, password=password)
        return user
