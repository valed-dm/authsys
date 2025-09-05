from django.urls import path

from .views_html import DeleteMeView
from .views_html import LoginPageView
from .views_html import LogoutPageView
from .views_html import MeView
from .views_html import RegisterPageView


app_name = "accounts_html"

urlpatterns = [
    # User-facing authentication pages
    path("register/", RegisterPageView.as_view(), name="register"),
    path("login/", LoginPageView.as_view(), name="login"),
    path("logout/", LogoutPageView.as_view(), name="logout"),
    # User account management pages
    path("me/", MeView.as_view(), name="me"),
    path("me/delete/", DeleteMeView.as_view(), name="delete_me"),
]
