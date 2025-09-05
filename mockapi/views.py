from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rbac.permissions import HasScope

from .serializers import OrderSerializer
from .serializers import ProjectSerializer


# ----------------------------
# Mock data (This is the core of the mock API)
# ----------------------------
FAKE_PROJECTS = [
    {"id": 1, "name": "Apollo"},
    {"id": 2, "name": "Zephyr"},
]

FAKE_ORDERS = [
    {"id": 101, "item": "Laptop", "quantity": 1},
    {"id": 102, "item": "Mouse", "quantity": 2},
]


# ----------------------------
# Projects Endpoints
# ----------------------------
class ProjectListView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "projects:read"

    def get(self, request):
        return Response(FAKE_PROJECTS)


class ProjectCreateView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "projects:create"

    def post(self, request):
        return Response({"status": "created"}, status=status.HTTP_201_CREATED)


class ProjectDeleteView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "projects:delete"

    def delete(self, request, pk):
        return Response(
            {"status": f"project {pk} deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


# ----------------------------
# Orders Endpoints
# ----------------------------
class OrderListView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "invoices:read"  # Note: Your permissions are for "invoices"

    def get(self, request):
        return Response(FAKE_ORDERS)


class OrderCreateView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "invoices:create"

    def post(self, request):
        return Response({"status": "order created"}, status=status.HTTP_201_CREATED)


class OrderDeleteView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, HasScope]
    required_scope = "invoices:delete"

    def delete(self, request, pk):
        return Response(
            {"status": f"order {pk} deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
