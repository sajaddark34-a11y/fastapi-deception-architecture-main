"""
Core Web Application Package (`core_web_app`).

Exports the primary FastAPI application (`app`) serving Layer 2 legitimate
enterprise endpoints and authentication services.
"""

from core_web_app.main import app

__all__ = [
    "app",
]
