# /rbac/serializers.py

"""
Defines the API data contracts (serializers) for the RBAC application.

These serializers control the JSON representation of the RBAC models,
handling both data validation for incoming requests and formatting for
outgoing responses.
"""

from typing import Any
from typing import Dict
from typing import List

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Action
from .models import Permission
from .models import Resource
from .models import Role
from .models import UserRole


# --- Read-Only Foundational Serializers ---
# These serializers are for displaying the building blocks of the RBAC system.


class ResourceSerializer(serializers.ModelSerializer):
    """A read-only serializer for the Resource model."""

    class Meta:
        model = Resource
        fields = ["id", "code", "description"]


class ActionSerializer(serializers.ModelSerializer):
    """A read-only serializer for the Action model."""

    class Meta:
        model = Action
        fields = ["id", "code", "description"]


class PermissionSerializer(serializers.ModelSerializer):
    """A read-only serializer for the Permission model."""

    # Use `source` to access attributes from related models.
    resource = serializers.CharField(source="resource.code", read_only=True)
    action = serializers.CharField(source="action.code", read_only=True)
    full_code = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Permission
        fields = ["id", "resource", "action", "full_code"]


# --- Core Management Serializers ---


class RoleSerializer(serializers.ModelSerializer):
    """

    A detailed serializer for the Role model.

    Used for both reading and writing (create/update) roles. For read
    operations, it includes a nested list of all permissions assigned to the role.
    """

    # Use a SerializerMethodField for full control over the nested representation.
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions"]

    @extend_schema_field(PermissionSerializer(many=True))
    def get_permissions(self, obj: Role) -> List[Dict[str, Any]]:
        """
        Resolves the 'permissions' field.

        This method efficiently retrieves and serializes the list of Permission
        objects associated with the given Role instance. It relies on the
        `prefetch_related` optimization in the corresponding ViewSet.
        """
        # Traverse the 'through' model to get to the actual Permission objects.
        permissions_list = [rp.permission for rp in obj.role_perms.all()]
        return PermissionSerializer(permissions_list, many=True).data


class AssignPermissionSerializer(serializers.Serializer):
    """
    A simple, write-only serializer for the `assign-permission` custom action.

    This is not a ModelSerializer; it's a plain Serializer used only for
    validating the input for a specific API action.
    """

    permission = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        write_only=True,
        help_text="The ID of the Permission to assign to the Role.",
    )

    class Meta:
        # Hides this from the main OpenAPI schema list as it's not a reusable component.
        ref_name = None


class UserRoleReadSerializer(serializers.ModelSerializer):
    """
    A read-only serializer for the User-Role assignment link.

    Provides detailed, nested information about both the user and the assigned role.
    """

    # Use `source` to get simple, readable string representations.
    role_name = serializers.CharField(source="role.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserRole
        fields = ["id", "user_id", "role_id", "user_email", "role_name"]


class UserRoleWriteSerializer(serializers.ModelSerializer):
    """
    A write-only serializer for creating a User-Role assignment link.

    Accepts simple foreign key IDs for the user and role.
    """

    class Meta:
        model = UserRole
        fields = ["user", "role"]
