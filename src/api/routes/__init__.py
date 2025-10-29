"""API route handlers."""

from .analyze import router as analyze_router
from .status import router as status_router
from .docs import router as docs_router
from .config import router as config_router
from .summary import router as summary_router

__all__ = [
    "analyze_router",
    "status_router",
    "docs_router",
    "config_router",
    "summary_router"
]
