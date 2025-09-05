from django.urls import reverse
import pytest


@pytest.mark.django_db
class TestAuthAPI:
    def test_register(self, api_client):
        """Tests successful user registration."""
        url = reverse("accounts_api:register_api")
        data = {
            "email": "newbie@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "Bie",
        }
        response = api_client.post(url, data=data)
        assert response.status_code == 201
        assert "access" in response.data
        assert response.data["user"]["email"] == "newbie@example.com"

    def test_login(self, api_client, user):
        """Tests successful user login."""
        url = reverse("accounts_api:login_api")
        data = {"email": user.email, "password": "testpassword123"}
        response = api_client.post(url, data=data)
        assert response.status_code == 200
        assert "access" in response.data

    def test_login_fail(self, api_client, user):
        """Tests that login fails with an incorrect password."""
        url = reverse("accounts_api:login_api")
        data = {"email": user.email, "password": "wrongpassword"}
        response = api_client.post(url, data=data)
        assert response.status_code == 401


@pytest.mark.django_db
class TestProfileAPI:
    def test_get_profile_unauthenticated(self, api_client):
        """Tests that anonymous users cannot access the profile view."""
        url = reverse("accounts_api:profile_api")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_get_profile_authenticated(self, user_api_client, user):
        """Tests that authenticated users can retrieve their own profile."""
        url = reverse("accounts_api:profile_api")
        response = user_api_client.get(url)
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_patch_profile(self, user_api_client, user):
        """Tests that a user can update their own profile."""
        url = reverse("accounts_api:profile_api")
        data = {"first_name": "Updated"}
        response = user_api_client.patch(url, data=data)
        assert response.status_code == 200
        assert response.data["first_name"] == "Updated"
        user.refresh_from_db()
        assert user.first_name == "Updated"
