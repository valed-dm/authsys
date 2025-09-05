from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction


User = get_user_model()


@transaction.atomic
def register_user(email: str, password: str, **extra_fields: Any) -> User:
    """
    Creates a new user with an email and password in a single database transaction.

    This service function is the single source of truth for user registration,
    ensuring that all new users are created consistently. It leverages the
    custom `UserManager.create_user` method.

    Args:
        email (str): The user's unique email address.
        password (str): The user's raw, unhashed password.
        **extra_fields (Any): Additional fields to be passed to the user model,
            such as `first_name` or `last_name`.

    Returns:
        User: The newly created and saved user instance.
    """

    user = User.objects.create_user(
        email=email,
        password=password,
        **extra_fields,
    )
    return user
