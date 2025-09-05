from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient

from rbac.models import Role


User = get_user_model()

# --- Core Fixtures (Available to all tests) ---


@pytest.fixture(scope="session", autouse=True)
def create_default_roles(django_db_setup, django_db_blocker):
    """
    Ensures the 'Default' and 'Admin' roles exist in the test database.
    Runs only once per test session for efficiency.
    """
    with django_db_blocker.unblock():
        Role.objects.get_or_create(name="Default")
        Role.objects.get_or_create(name="Admin")


@pytest.fixture
def user(db) -> User:
    """Creates and returns a standard user with the 'Default' role (via signal)."""
    return User.objects.create_user(
        email="testuser@example.com", password="testpassword123"
    )


@pytest.fixture
def admin_user(db) -> User:
    """Creates and returns an admin/superuser with the 'Admin' role (via signal)."""
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpassword123"
    )


# --- API Client Fixtures (Available to all tests) ---


@pytest.fixture
def api_client() -> APIClient:
    """Returns an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_api_client(api_client: APIClient, user: User) -> APIClient:
    """Returns an API client authenticated as a standard user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_api_client(api_client: APIClient, admin_user: User) -> APIClient:
    """Returns an API client authenticated as an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client
