"""
Defines serializers for the mock API endpoints.

These are not ModelSerializers; they are plain `serializers.Serializer` classes
used to describe the shape of the mock data structures for the purpose of
generating accurate OpenAPI/Swagger documentation.
"""

from rest_framework import serializers


class ProjectSerializer(serializers.Serializer):
    """
    Describes the structure of a Project object for the API documentation.
    """

    id = serializers.IntegerField(
        read_only=True, help_text="The unique ID of the project."
    )
    name = serializers.CharField(max_length=100, help_text="The name of the project.")


class OrderSerializer(serializers.Serializer):
    """
    Describes the structure of an Order object for the API documentation.
    """

    id = serializers.IntegerField(
        read_only=True, help_text="The unique ID of the order."
    )
    item = serializers.CharField(max_length=100, help_text="The item being ordered.")
    quantity = serializers.IntegerField(help_text="The quantity of the item.")
