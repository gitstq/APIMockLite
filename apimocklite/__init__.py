"""
🚀 APIMockLite - Lightweight AI-Powered API Mock Server

A zero-dependency, lightweight API mocking server with AI-powered response generation,
scenario switching, and request recording capabilities.

Author: gitstq
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .server import MockServer
from .config import Config
from .generator import ResponseGenerator
from .recorder import RequestRecorder

__all__ = ["MockServer", "Config", "ResponseGenerator", "RequestRecorder"]