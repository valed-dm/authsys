from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest


User = get_user_model()


@pytest.mark.django_db
class TestAdminUserManagement:
    def test_list_users_as_admin(self, admin_api_client):
        """Tests that an admin can successfully list users."""
        url = reverse("accounts_api:user-list")
        response = admin_api_client.get(url)
        assert response.status_code == 200
        # The paginated response has a 'results' key
        assert len(response.data["results"]) > 0

    def test_list_users_as_regular_user(self, user_api_client):
        """Tests that a regular user CANNOT list all users."""
        url = reverse("accounts_api:user-list")
        response = user_api_client.get(url)
        assert response.status_code == 403  # Forbidden

    def test_admin_can_restore_user(self, admin_api_client, user: User):
        """Tests that an admin can restore a soft-deleted user."""
        user.soft_delete()
        assert user.is_deleted is True

        url = reverse("accounts_api:restore_user", kwargs={"pk": user.pk})
        response = admin_api_client.post(url)

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_deleted is False

    def test_regular_user_cannot_restore(self, user_api_client, admin_user: User):
        """Tests that a regular user CANNOT restore another user."""
        admin_user.soft_delete()

        url = reverse("accounts_api:restore_user", kwargs={"pk": admin_user.pk})
        response = user_api_client.post(url)

        assert response.status_code == 403  # Forbidden
