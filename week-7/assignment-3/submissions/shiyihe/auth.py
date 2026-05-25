from fastapi import Header, HTTPException
from config import settings


def verify_api_key(api_key: str | None = Header(default=None)) -> str:
    if api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")

    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key
