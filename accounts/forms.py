from typing import Any
from typing import Dict
from typing import Optional

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.forms.renderers import TemplatesSetting
from django.forms.utils import ErrorList
from django.utils.html import format_html
from django.utils.html import format_html_join


User = get_user_model()


# --- User-Facing Forms (for HTML views) ---


class RegisterForm(forms.ModelForm):
    """
    Handles user registration via the standard HTML frontend.

    Includes email, name, and password fields, and ensures the password
    is properly hashed before saving the new user.
    """

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def save(self, commit: bool = True) -> User:
        """
        Creates and saves a new User instance from the form's validated data.

        Args:
            commit: If True, the user is saved to the database.

        Returns:
            The newly created user instance.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Handles user login via the standard HTML frontend.

    Validates user credentials (email and password) against the authentication
    backend and stores the authenticated user instance.
    """

    email = forms.EmailField(label="Email Address")
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
    )
    user: Optional[User] = None

    def clean(self) -> Dict[str, Any]:
        """
        Validates the form data and attempts to authenticate the user.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError(
                    "Invalid credentials. Please check your email and password."
                )
            self.user = user
        return cleaned_data

    def get_user(self) -> Optional[User]:
        """
        Returns the authenticated user if validation was successful.
        """
        return self.user


class UserUpdateForm(forms.ModelForm):
    """
    A simple form for users to update their own personal information.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


# --- Django Admin Customization Forms ---


class AdminErrorList(ErrorList):
    """
    Custom ErrorList that renders form errors as simple `<div>` tags.

    This is a technical workaround to prevent conflicts with global form
    rendering libraries (like crispy-forms) inside the Django admin,
    ensuring the admin's default styling is preserved.
    """

    def as_divs(self) -> str:
        """Renders the errors as a series of divs."""
        if not self:
            return ""
        return format_html(
            '<div class="errorlist">{}</div>',
            format_html_join(
                "",
                '<div class="error">{}</div>',
                ((e,) for e in self),
            ),
        )

    def __str__(self) -> str:
        """The default string representation for this error list."""
        return self.as_divs()


class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    """
    A custom authentication form for the Django admin site.

    Overrides the default form to use email as the `username` field for login,
    aligning the admin with the custom User model's `USERNAME_FIELD`.
    """

    # This ensures the form renders using Django's default engine,
    # isolating it from potential project-wide form rendering overrides.
    default_renderer = TemplatesSetting()

    # Override the 'username' field to be an EmailField.
    username = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Inject our custom error renderer.
        kwargs.setdefault("error_class", AdminErrorList)
        super().__init__(*args, **kwargs)
