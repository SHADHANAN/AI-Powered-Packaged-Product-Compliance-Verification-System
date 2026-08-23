from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from backend.config import get_settings
from backend.middleware.cors import setup_cors
from backend.middleware.error_handler import setup_error_handlers
from backend.routes import api_router
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown events.
    """
    settings = get_settings()
    logger.info(f"Starting {settings.APP_TITLE} (Environment: {settings.ENVIRONMENT})")
    logger.info(f"Docs available at http://{settings.HOST}:{settings.PORT}/docs")
    yield
    logger.info(f"Shutting down {settings.APP_TITLE}")


def create_app() -> FastAPI:
    """
    Application factory for the FastAPI backend.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Setup CORS middleware
    setup_cors(app, settings.CORS_ORIGINS)

    # Setup global exception handlers
    setup_error_handlers(app)

    # Register API routers with prefix (e.g. /api)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
