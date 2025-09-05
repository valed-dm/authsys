"""
Centralized, environment-aware application configuration.

This module uses `pydantic-settings` to load and validate application settings
from environment variables and a `.env` file. This provides a single source of
truth for all configuration, with type validation and clear defaults.

Attributes:
    BASE_DIR (Path): The absolute path to the project root directory.
    OUTPUT_DIR (Path): The directory for storing output files like logs.
    settings (Settings): A singleton instance of the validated settings class.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


# --- Directory Constants ---
BASE_DIR: Path = Path(__file__).resolve().parent.parent
OUTPUT_DIR: Path = BASE_DIR / "output"


class Settings(BaseSettings):
    """
    Defines and validates all environment variables for the application.

    Inherits from `pydantic_settings.BaseSettings` to automatically load values
    from the environment or the specified `.env` file. It also performs type
    casting and validation.
    """

    # Pydantic configuration: Load from .env file, case-insensitive.
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=False)

    APP_NAME: str = "AuthGuard"

    # --- Core Django Settings ---
    DJANGO_SECRET_KEY: str
    DEBUG: bool = True
    ALLOWED_HOSTS: List[str] = ["*"]

    # --- Database Connection ---
    PGDATABASE: str = "authsys"
    PGUSER: str = "postgres"
    PGPASSWORD: str = "postgres_default"
    PGHOST: str = "localhost"
    PGPORT: int = 5432

    # --- Custom JWT Generation (for core.jwt) ---
    # These settings are for the manual JWT generation in `core.jwt`.
    # `django-rest-framework-simplejwt` uses its own `SIMPLE_JWT` dictionary.
    JWT_SECRET: str
    JWT_ALG: str
    JWT_ACCESS_TTL: int  # Lifetime in seconds
    JWT_REFRESH_TTL: int  # Lifetime in seconds

    # --- Logging Configuration ---
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: Path = OUTPUT_DIR / "authsys.log"


# Create a single, validated instance of the settings to be imported by other modules.
settings = Settings()
