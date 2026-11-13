"""ASGI entry point for Uvicorn and Vercel."""

from backend.api import app

__all__ = ["app"]
