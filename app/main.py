from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging.config
from typing import Dict, Any
from datetime import datetime

# Internal imports
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.monitoring import get_sentry_service, SentryContextMiddleware
from app.core.middlewares import (
    RequestLoggingMiddleware,
    ResponseTimeMiddleware,
    RequestIDMiddleware,
    RateLimitMiddleware,
    CacheMiddleware,
)
from app.core.db import mongodb
from app.core.config.logging import LoggingSettings
from app.api.v1.routes import create_api_router

logging_settings = LoggingSettings()
logging.config.dictConfig(logging_settings.get_logging_config())
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("Starting up application...")
    
    if settings.logging.SENTRY_ENABLED:
        sentry_service = get_sentry_service()
        sentry_service.initialize()
        logger.info("Sentry initialized successfully")

    try:
        logger.info("Attempting to connect to MongoDB...")
        await mongodb.connect_to_mongodb(
            settings.db.MONGODB_URL,
            **settings.db.mongodb_connection_params
        )
        app.mongodb_client = mongodb.client
        app.mongodb = app.mongodb_client[settings.db.MONGODB_DB_NAME]
        logger.info("Successfully connected to MongoDB")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
        raise

    try:
        await startup_tasks(app)
    except Exception as e:
        logger.error(f"Error during startup tasks: {str(e)}", exc_info=True)
        raise

    api_router = create_api_router()
    app.include_router(api_router, prefix='/api/v1')
    yield

    logger.info("Shutting down application...")

    try:
        await mongodb.close_mongodb_connection()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}", exc_info=True)

    try:
        await cleanup_tasks(app)
    except Exception as e:
        logger.error(f"Error during cleanup tasks: {str(e)}", exc_info=True)

async def startup_tasks(app: FastAPI) -> None:
    """Additional startup tasks"""
    # Initialize any background tasks
    # Setup any additional services
    pass

async def cleanup_tasks(app: FastAPI) -> None:
    """Additional cleanup tasks"""
    # Cleanup any background tasks
    # Cleanup any additional services
    pass

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app.PROJECT_NAME,
        description=settings.app.DESCRIPTION,
        version=settings.app.VERSION,
        docs_url=settings.app.DOCS_URL,
        redoc_url=settings.app.REDOC_URL,
        openapi_url=settings.app.OPENAPI_URL,
        lifespan=lifespan,
        debug=settings.app.DEBUG
    )

    setup_exception_handlers(app)
    setup_middlewares(app)
    setup_base_routes(app)
    setup_event_handlers(app)

    return app

def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.app.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.app.ALLOWED_HOSTS
    )

    app.add_middleware(
        GZipMiddleware, 
        minimum_size=settings.app.MIDDLEWARE_GZIP_MINIMUM_SIZE
    )

    if settings.logging.SENTRY_ENABLED:
        app.add_middleware(SentryContextMiddleware)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ResponseTimeMiddleware)

    if settings.app.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)

    if settings.cache.ENABLED:
        app.add_middleware(CacheMiddleware)

def setup_base_routes(app: FastAPI) -> None:
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "version": settings.app.VERSION,
            "environment": settings.app.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }

def setup_event_handlers(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id_to_response(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Request-ID"] = str(request.state.request_id)
        return response

app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        workers=settings.app.WORKERS_COUNT,
        log_config=settings.logging.get_logging_config()
    )

application = app
