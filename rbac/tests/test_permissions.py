from django.views import View
import pytest
from rest_framework.test import APIRequestFactory

from rbac.permissions import HasScope


@pytest.fixture
def rf() -> APIRequestFactory:
    """A fixture for Django's RequestFactory."""
    return APIRequestFactory()


@pytest.fixture
def mock_view() -> View:
    """A mock view with a required_scope attribute."""
    view = View()
    view.required_scope = "projects:read"
    return view


@pytest.mark.django_db
def test_has_scope_permission_success(rf, user, mock_view):
    """Tests that the permission passes if the user has the required scope."""
    permission = HasScope()
    request = rf.get("/")
    request.user = user
    # Manually attach the scopes that the middleware would
    user.scopes = {"projects": ["read", "create"]}

    assert permission.has_permission(request, mock_view) is True


@pytest.mark.django_db
def test_has_scope_permission_fail(rf, user, mock_view):
    """Tests that the permission fails if the user does NOT have the scope."""
    permission = HasScope()
    request = rf.get("/")
    request.user = user
    # Give the user a different scope
    user.scopes = {"invoices": ["read"]}

    assert permission.has_permission(request, mock_view) is False


@pytest.mark.django_db
def test_has_scope_superuser_bypass(rf, admin_user, mock_view):
    """Tests that a superuser always has permission, regardless of scopes."""
    permission = HasScope()
    request = rf.get("/")
    request.user = admin_user
    # The admin has no scopes attached, but should still pass
    admin_user.scopes = {}

    assert permission.has_permission(request, mock_view) is True
