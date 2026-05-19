"""API key authentication for protected endpoints."""
from typing import Optional

from fastapi import Header, HTTPException

from config import settings


def verify_api_key(api_key: Optional[str] = Header(None, alias="api-key")) -> str:
    """Verify the 'api-key' request header.

    Returns 403 when the header is missing and 401 when the key is wrong.
    """
    if api_key is None:
        raise HTTPException(status_code=403, detail="Missing API key")
    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
