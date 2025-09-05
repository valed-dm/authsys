from django.utils import timezone
import pytest

from accounts.models import User


@pytest.mark.django_db
def test_user_soft_delete(user: User):
    """Tests that the soft_delete method correctly deactivates a user."""
    assert user.is_active is True
    assert user.is_deleted is False
    assert user.deleted_at is None

    user.soft_delete()

    refreshed_user = User.objects.get(id=user.id)
    assert refreshed_user.is_active is False
    assert refreshed_user.is_deleted is True
    assert refreshed_user.deleted_at is not None
    assert (timezone.now() - refreshed_user.deleted_at).total_seconds() < 5


@pytest.mark.django_db
def test_user_restore(user: User):
    """Tests that the restore method correctly reactivates a user."""
    user.soft_delete()
    assert user.is_active is False
    assert user.is_deleted is True

    user.restore()

    refreshed_user = User.objects.get(id=user.id)
    assert refreshed_user.is_active is True
    assert refreshed_user.is_deleted is False
    assert refreshed_user.deleted_at is None
