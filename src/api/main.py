"""FastAPI server for AI Documentation Generator."""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import (
    analyze_router,
    status_router,
    docs_router,
    config_router,
    summary_router
)
from .core.config_manager import get_server_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting AI Documentation Generator API")
    os.makedirs(os.getenv("UPLOAD_DIR", "uploads"), exist_ok=True)
    yield
    logger.info("Shutting down AI Documentation Generator API")


app = FastAPI(
    title="AI Documentation Generator API",
    description="""
    RESTful API for automated documentation generation using local AI.
    
    This API provides endpoints to:
    - Analyze projects and generate comprehensive documentation
    - Monitor task progress in real-time
    - Retrieve generated documentation files
    - Manage configuration settings
    - Get AI-generated project summaries
    
    Powered by Ollama, LangChain, and LangGraph.
    """,
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "AI Documentation Generator",
        "url": "https://github.com/yourusername/ai-doc-generator",
    },
    license_info={
        "name": "MIT",
    }
)

server_config = get_server_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config['cors_origins'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(status_router)
app.include_router(docs_router)
app.include_router(config_router)
app.include_router(summary_router)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and version information.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0",
            "service": "AI Documentation Generator API"
        }
    )


@app.get("/info", tags=["info"])
async def get_info():
    """
    Get API information and capabilities.
    
    Returns details about available features and configuration.
    """
    return JSONResponse(
        content={
            "name": "AI Documentation Generator API",
            "version": "1.0.0",
            "description": "RESTful API for automated documentation generation",
            "features": [
                "Project analysis and documentation generation",
                "ZIP file upload support",
                "Async task processing with progress tracking",
                "Configurable AI models and settings",
                "Multiple output formats (Markdown)",
                "Comprehensive OpenAPI documentation"
            ],
            "endpoints": {
                "analyze": "POST /analyze - Start documentation generation",
                "status": "GET /status/{task_id} - Check task progress",
                "docs": "GET /docs/{task_id} - Retrieve generated documentation",
                "config": "GET /config - View/update configuration",
                "summary": "GET /summary/{task_id} - Get project summary"
            },
            "documentation": {
                "swagger": "/",
                "redoc": "/redoc"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    config = get_server_config()
    uvicorn.run(
        "src.api.main:app",
        host=config['host'],
        port=config['port'],
        reload=config['reload'],
        log_level=config['log_level']
    )
