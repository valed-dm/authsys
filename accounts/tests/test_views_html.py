from django.test import Client
from django.urls import reverse
import pytest

from accounts.models import User


@pytest.fixture
def client() -> Client:
    """A fixture for Django's test client."""
    return Client()


@pytest.mark.django_db
class TestHTMLLoginLogout:
    def test_login_page_loads(self, client):
        """Tests that the login page returns a 200 OK status."""
        url = reverse("accounts_html:login")
        response = client.get(url)
        assert response.status_code == 200

    def test_successful_login_and_logout(self, client, user: User):
        """Tests the full login and logout flow for the HTML views."""
        # Test Login
        login_url = reverse("accounts_html:login")
        login_data = {"email": user.email, "password": "testpassword123"}
        response = client.post(login_url, login_data, follow=True)

        assert response.status_code == 200
        # After a successful login, we should be on the 'me' page
        assert response.resolver_match.view_name == "accounts_html:me"
        # Check that a success message was displayed
        assert "Login successful!" in str(response.content)

        # Test Logout
        logout_url = reverse("accounts_html:logout")
        response = client.get(logout_url, follow=True)
        assert response.status_code == 200
        # After logout, we should be back on the login page
        assert response.resolver_match.view_name == "accounts_html:login"
        assert "You have been successfully logged out." in str(response.content)


@pytest.mark.django_db
class TestHTMLProfileUpdate:
    def test_update_profile(self, client, user: User):
        """Tests that a logged-in user can update their profile via the HTML form."""
        # First, log the user in
        client.login(email=user.email, password="testpassword123")

        me_url = reverse("accounts_html:me")
        update_data = {"first_name": "NewFirstName", "last_name": "NewLastName"}

        response = client.post(me_url, update_data, follow=True)

        assert response.status_code == 200
        assert "Your profile has been updated successfully!" in str(response.content)

        user.refresh_from_db()
        assert user.first_name == "NewFirstName"
        assert user.last_name == "NewLastName"
