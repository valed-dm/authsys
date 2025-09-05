"""
Configures the Loguru logger to be the primary logging backend for the application.

This module provides a single setup function that replaces Django's default
logging with the more powerful and developer-friendly Loguru library.
"""

import sys
from typing import NoReturn

from loguru import logger
from loguru._logger import Logger

from .config import OUTPUT_DIR
from .config import settings


def setup_logging() -> Logger:
    """
    Initializes and configures the Loguru logger for the entire application.

    This function should be called once at the application's entry point
    (e.g., in `settings.py`). It sets up two primary "sinks": one for writing
    detailed, structured logs to a file, and another for writing colorful,
    human-readable logs to the console.

    Returns:
        The configured Loguru logger instance.
    """
    # 1. Remove the default handler to ensure no duplicate logs.
    logger.remove()

    # 2. Safely create the log directory if it doesn't exist.
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # If the log directory cannot be created, it's a critical startup error.
        # Log to stderr and exit to prevent the app from running without logging.
        _critical_exit(f"Failed to create log directory {OUTPUT_DIR}: {e}")

    # 3. Configure the file sink for detailed, persistent logging.
    #    - `enqueue=True` makes logging non-blocking, which is crucial for performance.
    #    - `rotation` automatically manages log file size.
    #    - `backtrace` and `diagnose` provide rich debugging info in DEBUG mode.
    logger.add(
        sink=settings.LOG_FILE,
        level=settings.LOG_LEVEL.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
            "{name}:{function}:{line} - {message}"
        ),
        rotation="1 MB",
        enqueue=True,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
        catch=True,  # Catches exceptions from within Loguru sinks
    )

    # 4. Configure the console sink for readable development output.
    #    Uses colors and a simpler format for a better developer experience.
    logger.add(
        sink=sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level:<8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        ),
        colorize=True,
    )

    # 5. Return the configured logger instance.
    return logger


def _critical_exit(message: str) -> NoReturn:
    """
    A helper function to print a critical error to stderr and exit the program.

    Used for unrecoverable startup errors.
    """
    sys.stderr.write(f"FATAL: {message}\n")
    sys.exit(1)
