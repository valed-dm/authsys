#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This script is the primary entry point for running management commands
such as `runserver`, `migrate`, `createsuperuser`, etc. It sets up the
necessary environment for Django to run.
"""

import os
import sys


def main() -> None:
    """
    Sets up the environment and executes Django management commands.

    This function configures the `DJANGO_SETTINGS_MODULE` environment variable
    and then delegates the execution to Django's `execute_from_command_line`.

    It also provides a helpful error message if Django is not installed or the
    virtual environment is not activated.
    """

    # Point Django to the project's settings file.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authsys.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # This is a common error for new developers, so the message is explicit.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Pass the command-line arguments (e.g., ['manage.py', 'runserver']) to Django.
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
