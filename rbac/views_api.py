"""
Provides the API views (ViewSets) for the RBAC application.

This module defines the endpoints for administrators to manage the core
components of the Role-Based Access Control system, such as Roles,
Permissions, and their assignments.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Action
from .models import Permission
from .models import Resource
from .models import Role
from .models import RolePermission
from .serializers import ActionSerializer
from .serializers import AssignPermissionSerializer
from .serializers import PermissionSerializer
from .serializers import ResourceSerializer
from .serializers import RoleSerializer


# --- Read-Only Foundational ViewSets ---
# These models are the building blocks of the RBAC system. They are typically
# managed via data migrations and presented here as read-only for inspection.


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Resources."""

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAdminUser]


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Actions."""

    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [permissions.IsAdminUser]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Permissions."""

    queryset = Permission.objects.all().select_related("resource", "action")
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]


# --- Role Management ViewSet ---


class RoleViewSet(viewsets.ModelViewSet):
    """

    API endpoint to Create, List, Retrieve, Update (PATCH), and Delete Roles.

    This is the primary administrative endpoint for managing roles and their
    associated permissions via a custom action.
    """

    queryset = Role.objects.all().prefetch_related(
        "role_perms__permission__resource", "role_perms__permission__action"
    )
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]
    # Whitelist of allowed HTTP methods. Excludes the less-flexible 'put'.
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @extend_schema(
        request=AssignPermissionSerializer,
        summary="Assign a permission to a role",
        description="Assigns a single existing permission to this role."
                    " This operation is idempotent.",
    )
    @action(detail=True, methods=["post"], url_path="assign-permission")
    def assign_permission(self, request: Request, pk: int = None) -> Response:
        """A custom action to assign a single permission to a role."""
        role: Role = self.get_object()
        serializer = AssignPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Because we used PrimaryKeyRelatedField, validated_data['permission']
        # is a full, validated Permission object.
        permission: Permission = serializer.validated_data["permission"]

        # Use get_or_create on the 'through' model to create the link.
        RolePermission.objects.get_or_create(role=role, permission=permission)

        # Return the complete, updated Role object.
        return Response(self.get_serializer(role).data, status=status.HTTP_200_OK)
