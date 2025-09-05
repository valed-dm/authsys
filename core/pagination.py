"""
Provides a custom pagination class for Django REST Framework.

This module defines a project-wide standard for the structure of paginated
API responses, ensuring consistency across all list endpoints.
"""

from typing import Any
from typing import List
from typing import Optional

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    A custom pagination class that provides a structured, envelope-style response.

    This class overrides the default pagination output to include metadata such as
    total counts, page numbers, and navigation links, which is a common best
    practice for modern APIs. It also allows clients to request a different page
    size via a query parameter.
    """

    # The name of the query parameter that allows clients to override the default
    # page size.
    # Example: /api/users/?page_size=25
    page_size_query_param: str = "page_size"

    # The maximum page size that a client is allowed to request.
    # This prevents performance issues from requests for excessively large pages.
    max_page_size: int = 100

    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        Constructs the paginated response with a custom structure.

        Args:
            data: A list of serialized data objects for the current page.

        Returns:
            A DRF Response object with the structured pagination envelope.
        """
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
            }
        )

    def get_next_link(self) -> Optional[str]:
        return super().get_next_link()

    def get_previous_link(self) -> Optional[str]:
        return super().get_previous_link()
