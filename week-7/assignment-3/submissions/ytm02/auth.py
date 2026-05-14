"""API key authentication for protected endpoints."""
import os
import logging
from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)


def verify_api_key(api_key: str = Header(..., alias="api-key")) -> str:
    """Validate the API key provided in the request header.

    Args:
        api_key: Value from the 'api-key' request header.

    Returns:
        The validated API key string.

    Raises:
        HTTPException: 401 if key is missing or invalid.
    """
    expected = os.getenv("API_KEY", "")
    if not expected:
        logger.warning("API_KEY environment variable is not set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API key not set",
        )
    if api_key != expected:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key
