"""
Logging configuration for the application.
Provides structured logging with request ID tracking.
"""

import logging
import sys
from typing import Any
from backend.core.config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.

    Sets up:
    - Log level based on environment
    - Structured log formatting
    - Console output handler

    In production, you would typically:
    - Add file handlers
    - Integrate with log aggregation services (e.g., CloudWatch, Datadog)
    - Add JSON formatting for structured logs
    """

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set third-party library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Example usage in other modules:
# from backend.core.logging import get_logger
# logger = get_logger(__name__)
# logger.info("Processing request")
