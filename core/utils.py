# /core/utils.py

"""
A collection of general-purpose, project-agnostic utility functions.

This module provides common helper functions that can be reused across
different applications within the project.
"""

import uuid
from typing import List, Generator, TypeVar
from django.utils.text import slugify

# A TypeVar allows us to create generic functions. 'T' can be any type.
T = TypeVar("T")


def generate_uuid() -> str:
    """
    Generates a random, URL-safe Version 4 UUID as a string.

    Useful for creating unique, non-sequential identifiers for model instances
    or other objects.

    Returns:
        A string representation of a new UUIDv4.
    """
    return str(uuid.uuid4())


def slugify_text(text: str, allow_unicode: bool = False) -> str:
    """
    A consistent wrapper around Django's slugify utility.

    Converts a string into a URL-friendly "slug" by removing or converting
    unsafe characters (e.g., "Hello World!" becomes "hello-world").

    Args:
        text: The input string to be slugified.
        allow_unicode: If True, allows Unicode characters in the output.
                       Defaults to False for maximum compatibility.

    Returns:
        The slugified string.
    """
    return slugify(text, allow_unicode=allow_unicode)


def chunk_list(data: List[T], chunk_size: int) -> Generator[List[T], None, None]:
    """
    An efficient generator to yield successive n-sized chunks from a list.

    This is useful for processing large lists in batches to conserve memory,
    for example, when using Django's `bulk_create` or `bulk_update`.

    Args:
        data: The list of items to be chunked.
        chunk_size: The desired maximum size of each chunk.

    Yields:
        A list containing a chunk of items from the original list.

    Example:
        >>> my_list = [1, 2, 3, 4, 5, 6, 7]
        >>> for chunk in chunk_list(my_list, 3):
        ...     print(chunk)
        [1, 2, 3]
        [4, 5, 6]
        [7]
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]
