"""
URL configuration for the RBAC (Role-Based Access Control) API.

This module uses Django REST Framework's `DefaultRouter` to automatically
generate a full suite of RESTful URL patterns for the RBAC ViewSets.
"""

from django.urls import include
from django.urls import path
from rest_framework.routers import BaseRouter
from rest_framework.routers import DefaultRouter

from . import views_api


app_name: str = "rbac_api"

# A router provides an easy way of automatically determining the URL conf.
router: BaseRouter = DefaultRouter()

# Register the ViewSets with the router. This will generate URLs like:
# /roles/, /roles/{id}/, /roles/{id}/assign-permission/, etc.
router.register(r"roles", views_api.RoleViewSet, basename="role")
router.register(r"permissions", views_api.PermissionViewSet, basename="permission")
router.register(r"resources", views_api.ResourceViewSet, basename="resource")
router.register(r"actions", views_api.ActionViewSet, basename="action")

# The API URLs are determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
