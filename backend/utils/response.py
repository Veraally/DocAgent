"""Unified JSON response helpers."""

from typing import Any


def success_response(message: str = "OK", data: Any = None) -> dict[str, Any]:
    """Build a success response with consistent format.

    Args:
        message: Human-readable success message.
        data: Optional payload to include in the response.

    Returns:
        A dict with ``success=True``, a message, and optional data.
    """
    response: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


def error_response(message: str = "Error", data: Any = None) -> dict[str, Any]:
    """Build an error response with consistent format.

    Args:
        message: Human-readable error message.
        data: Optional payload (e.g. validation details).

    Returns:
        A dict with ``success=False``, a message, and optional data.
    """
    response: dict[str, Any] = {"success": False, "message": message}
    if data is not None:
        response["data"] = data
    return response
