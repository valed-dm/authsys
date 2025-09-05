"""
URL configuration for the Mock API application.

This module defines the URL patterns for the mock endpoints, which are used
to demonstrate and test the RBAC permission system against non-database-backed
resources.
"""

from typing import List

from django.urls import path
from django.urls.resolvers import URLPattern

from .views import OrderCreateView
from .views import OrderDeleteView
from .views import OrderListView
from .views import ProjectCreateView
from .views import ProjectDeleteView
from .views import ProjectListView


app_name: str = "mockapi"

urlpatterns: List[URLPattern] = [
    # --- Projects Endpoints ---
    path("projects/", ProjectListView.as_view(), name="projects-list"),
    path("projects/create/", ProjectCreateView.as_view(), name="projects-create"),
    path(
        "projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="projects-delete"
    ),
    # --- Orders Endpoints ---
    path("orders/", OrderListView.as_view(), name="orders-list"),
    path("orders/create/", OrderCreateView.as_view(), name="orders-create"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="orders-delete"),
]
