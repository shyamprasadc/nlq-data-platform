"""
Utility helper functions.
Common utilities used across the application.
"""

from datetime import datetime
from typing import Any, Dict


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime object to format
        format_string: Format string (default: ISO-like format)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_string)


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize a string by removing excessive whitespace and limiting length.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    # Remove excessive whitespace
    sanitized = " ".join(text.split())

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def build_response(success: bool, message: str, data: Any = None) -> Dict[str, Any]:
    """
    Build a standardized API response.

    Args:
        success: Whether the operation was successful
        message: Response message
        data: Optional response data

    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "message": message,
    }

    if data is not None:
        response["data"] = data

    return response


def paginate_query_params(page: int = 1, page_size: int = 20) -> tuple[int, int]:
    """
    Convert page-based pagination to skip/limit.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Tuple of (skip, limit) for database queries
    """
    skip = (page - 1) * page_size
    limit = page_size

    return skip, limit
