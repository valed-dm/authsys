from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from rbac.models import Permission
from rbac.models import Role
from rbac.models import UserRole


User = get_user_model()


# --- Authentication Serializers ---


class LoginSerializer(serializers.Serializer):
    """
    Validates user credentials for the API login endpoint.

    This is a write-only serializer used to process the request body.
    """

    email = serializers.EmailField(write_only=True, help_text="User's email address.")
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        help_text="User's password.",
    )

    class Meta:
        ref_name = "UserLogin"  # Gives a clear name in the Swagger UI schema list


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration via the API.

    Validates user data and creates a new user instance with a hashed password.
    """

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password")

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Creates a new user instance using the custom user manager."""
        return User.objects.create_user(**validated_data)


# --- User Profile & Data Serializers ---


class ProfileSerializer(serializers.ModelSerializer):
    """
    Represents the public-facing profile of a user.

    Used for retrieving a user's own profile (`/me/`) or for admin views of users.
    Excludes sensitive or internal data.
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "email", "date_joined")


class UpdateMeSerializer(serializers.ModelSerializer):
    """

    Validates data for a user updating their OWN profile.

    Only includes fields that are safe for a user to modify themselves.
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name")


class UserSerializer(serializers.ModelSerializer):
    """
    A detailed, read-only representation of a user, including their RBAC role
     and permissions.
    """

    role = serializers.SerializerMethodField(
        help_text="The user's primary assigned role."
    )
    permissions = serializers.SerializerMethodField(
        help_text="A flattened list of all unique permission codes from the user's"
                  " roles."
    )

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "permissions")

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_role(self, obj: User) -> Optional[str]:
        """
        Returns the name of the user's first assigned role by querying the DB.
        """
        # This will always hit the database for the latest truth.
        user_role = UserRole.objects.filter(user=obj).select_related("role").first()
        return user_role.role.name if user_role else None

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_permissions(self, obj: User) -> List[str]:
        """
        Returns a sorted list of unique permission codes for the user by querying the DB.
        """
        # This queryset is guaranteed to get the latest data from the database,
        # reflecting any changes made by signals.
        permissions = (
            Permission.objects.filter(
                perm_roles__role__in=obj.user_roles.values("role")
            )
            .select_related("resource", "action")
            .distinct()
        )

        perms = [str(p) for p in permissions]

        return sorted(perms)


# --- Admin-Specific Serializers ---


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Validates data for an ADMIN updating another user's profile.

    Includes administrative fields like `is_active` and `is_staff`.
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_active", "is_staff")


class AssignRoleSerializer(serializers.Serializer):
    """
    A simple, write-only serializer for the `assign-role` custom action.

    Validates that a given `role_id` corresponds to an existing Role.
    """

    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        help_text="The ID of the Role to assign to the User.",
    )

    class Meta:
        ref_name = (
            None  # Hides this from the main schema list as it's for a specific action
        )


class DeletedUserSerializer(serializers.ModelSerializer):
    """
    A read-only serializer for displaying soft-deleted users.
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_joined", "deleted_at")

