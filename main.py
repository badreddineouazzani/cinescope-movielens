"""ASGI entry point for Uvicorn and Vercel."""

from api_service.api import app

__all__ = ["app"]
