from typing import Any
from typing import Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import LoginForm
from .forms import RegisterForm
from .forms import UserUpdateForm
from .mixins import JWTContextMixin


User = get_user_model()
API_BASE_URL = "/api/accounts/"  # DRF endpoints


class HomePageView(View):
    """
    Handles the root URL ('/').

    Redirects authenticated users to their main account page and anonymous
    users to the login page.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("accounts_html:me")  # Corrected redirect
        return redirect("accounts_html:login")


class RegisterPageView(View):
    """
    Handles the user registration page (GET) and form submission (POST).

    On successful registration, it logs the user in, stores their JWTs in the
    session, and redirects them to their account page.
    """

    template_name = "accounts/register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = RegisterForm(request.POST)
        if form.is_valid():
            # The RegisterForm already handles user creation and password hashing.
            user = form.save()

            # Log the new user in immediately.
            login(request, user)

            # Generate JWTs and store them in the session for API access.
            refresh = RefreshToken.for_user(user)
            request.session["access_token"] = str(refresh.access_token)
            request.session["refresh_token"] = str(refresh)

            messages.success(request, "Registration successful! You are now logged in.")
            return redirect("accounts_html:me")  # Corrected redirect

        # If form is invalid, re-render the page with errors.
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form})


class LoginPageView(View):
    """
    Handles the user login page (GET) and credential validation (POST).
    """

    template_name = "accounts/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            refresh = RefreshToken.for_user(user)
            request.session["access_token"] = str(refresh.access_token)
            request.session["refresh_token"] = str(refresh)

            messages.success(request, "Login successful!")
            return redirect("accounts_html:me")  # Corrected redirect

        # If form is invalid, LoginForm's clean method adds the error.
        return render(request, self.template_name, {"form": form})


class LogoutPageView(View):
    """
    Handles user logout for both GET and POST requests.

    Clears the Django session and removes JWTs to securely log the user out.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        return self._logout_user(request)

    def post(self, request: HttpRequest) -> HttpResponse:
        return self._logout_user(request)

    def _logout_user(self, request: HttpRequest) -> HttpResponse:
        """Private helper to perform the logout logic."""
        request.session.pop("access_token", None)
        request.session.pop("refresh_token", None)
        logout(request)
        messages.info(request, "You have been successfully logged out.")
        return redirect("accounts_html:login")


class MeView(LoginRequiredMixin, JWTContextMixin, View):
    """
    The primary user account management page.

    GET: Displays user info and a form to update their personal data.
    POST: Processes the form submission to update the user's profile.
    """

    template_name = "accounts/me.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Builds a consistent context dictionary for the template."""
        context = super().get_context_data(**kwargs)  # From JWTContextMixin
        context["user"] = self.request.user
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        if getattr(request.user, "is_deleted", False):
            messages.warning(request, "Your account is inactive or deleted.")
            return self._logout_user(request)  # Log out deleted users

        update_form = UserUpdateForm(instance=request.user)
        context = self.get_context_data(update_form=update_form)
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        update_form = UserUpdateForm(request.POST, instance=request.user)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts_html:me")

        messages.error(request, "Please correct the errors below.")
        context = self.get_context_data(update_form=update_form)
        return render(request, self.template_name, context)


class DeleteMeView(LoginRequiredMixin, View):
    """
    Handles the POST request to soft-delete the currently logged-in user.
    """

    template_name = "accounts/account_deleted.html"
    login_url = "/accounts/login/"

    def post(self, request: HttpRequest) -> HttpResponse:
        user: User = request.user
        user.soft_delete()

        # Securely log the user out after deletion.
        request.session.pop("access_token", None)
        request.session.pop("refresh_token", None)
        logout(request)

        return render(request, self.template_name)
