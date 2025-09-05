from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from authsys.settings import log
from rbac.models import UserRole

from .serializers import AdminUserUpdateSerializer
from .serializers import AssignRoleSerializer
from .serializers import DeletedUserSerializer
from .serializers import LoginSerializer
from .serializers import ProfileSerializer
from .serializers import UpdateMeSerializer
from .serializers import UserRegisterSerializer
from .serializers import UserSerializer


User = get_user_model()


# --- Authentication Views ---

@extend_schema(
    summary="Register a new user",
    description="Registers a user and returns their profile and JWT tokens.",
    request=UserRegisterSerializer,
    responses={201: {"description": "User created successfully."}},
    tags=["Authentication"] # Group in Swagger
)
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            "user": ProfileSerializer(user).data, # Return the simple Profile
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return Response(data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Login a user",
    description="Authenticates a user and returns their profile and JWT tokens.",
    request=LoginSerializer,
    responses={
        200: {"description": "Login successful."},
        401: {"description": "Invalid credentials"},
    },
    tags=["Authentication"]
)
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: Any) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": ProfileSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# --- "Me" (Current User) Views ---

@extend_schema(
    summary="Get or update my profile",
    description="Retrieve (GET) or partially update (PATCH) the authenticated user's"
                " profile.",
    request=UpdateMeSerializer,
    responses={200: ProfileSerializer},
    tags=["Profile (Me)"]
)
class ProfileAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView,
):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    def get_serializer_class(self) -> Any:
        if self.request.method == "PATCH":
            return UpdateMeSerializer
        return super().get_serializer_class()

    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data)


@extend_schema(
    summary="Get my permissions",
    responses={200: UserSerializer},
    tags=["Profile (Me)"],
)
class MyPermissionsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return User.objects.prefetch_related(
            "user_roles__role__role_perms__permission__resource",
            "user_roles__role__role_perms__permission__action",
        ).get(id=self.request.user.id)


@extend_schema(
    summary="Soft-delete my account",
    request={"application/json": {"properties": {"refresh": {"type": "string"}}}},
    responses={204: "Account soft-deleted."},
    tags=["Profile (Me)"]
)
class SoftDeleteMeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        user.soft_delete()
        refresh_token_str = request.data.get("refresh")
        if refresh_token_str:
            try:
                RefreshToken(refresh_token_str).blacklist()
            except TokenError as e:
                log.warning(f"Failed to blacklist token for {user.email}: {e}")
            except Exception:
                log.error(
                    f"Unexpected error blacklisting token for {user.email}",
                    exc_info=True,
                )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Admin: User Management Views ---

class UserViewSet(viewsets.ModelViewSet):
    """Admin-only endpoint for managing users."""
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self) -> Any:
        if self.action == "create":
            return UserRegisterSerializer
        if self.action in ["update", "partial_update"]:
            return AdminUserUpdateSerializer
        return ProfileSerializer

    @extend_schema(request=AssignRoleSerializer, summary="Assign a role to this user")
    @action(detail=True, methods=["post"], url_path="assign-role")
    def assign_role(self, request: Any, pk: int = None) -> Response:
        user = self.get_object()
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data["role"]
        UserRole.objects.get_or_create(user=user, role=role)
        return Response(ProfileSerializer(user).data)


@extend_schema(
    summary="List superusers",
    responses={200: ProfileSerializer(many=True)},
    tags=["Admin"]
)
class SuperuserListAPIView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.filter(is_superuser=True)


@extend_schema(
    summary="List soft-deleted users",
    responses={200: DeletedUserSerializer(many=True)},
    tags=["Admin"]
)
class DeletedUsersListAPIView(generics.ListAPIView):
    serializer_class = DeletedUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.filter(is_deleted=True)


@extend_schema(
    summary="Restore a soft-deleted user",
    request=None,
    responses={200: {"description": "User restored."}},
    tags=["Admin"]
)
class RestoreUserAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request: Any, pk: int) -> Response:
        try:
            user = User.objects.get(pk=pk, is_deleted=True)
            user.restore()
            return Response({"detail": f"User {user.email} restored successfully."})
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found or not deleted."},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="Permanently delete a user",
    responses={204: "User permanently deleted."},
    tags=["Admin"]
)
class PermanentDeleteUserAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
