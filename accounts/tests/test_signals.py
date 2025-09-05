import pytest

from rbac.models import UserRole


@pytest.mark.django_db
def test_regular_user_gets_default_role(user):
    """
    Tests that the post_save signal correctly assigns the 'Default' role
    to a newly created regular user.
    """
    assert UserRole.objects.filter(user=user, role__name="Default").exists()
    assert not UserRole.objects.filter(user=user, role__name="Admin").exists()


@pytest.mark.django_db
def test_superuser_gets_admin_role(admin_user):
    """
    Tests that the post_save signal correctly assigns the 'Admin' role
    to a newly created superuser.
    """
    assert UserRole.objects.filter(user=admin_user, role__name="Admin").exists()
