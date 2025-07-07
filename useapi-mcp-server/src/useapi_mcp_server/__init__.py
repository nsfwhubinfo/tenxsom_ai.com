"""
UseAPI.net MCP Server

A comprehensive Model Context Protocol server for UseAPI.net AI services.
"""

from .server import UseAPIServer
from .config import UseAPIConfig
from .exceptions import (
    UseAPIError,
    UseAPIAuthenticationError,
    UseAPIRateLimitError,
    UseAPITimeoutError,
    UseAPINotFoundError,
)

__version__ = "1.0.0"
__author__ = "Tenxsom AI"
__email__ = "goldensonproperties@gmail.com"

__all__ = [
    "UseAPIServer",
    "UseAPIConfig", 
    "UseAPIError",
    "UseAPIAuthenticationError",
    "UseAPIRateLimitError", 
    "UseAPITimeoutError",
    "UseAPINotFoundError",
]