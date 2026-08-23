from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.utils.logger import logger


def setup_error_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for standardized error responses.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning(
            f"HTTP error occurred: status_code={exc.status_code}, "
            f"path={request.url.path}, detail={exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
                    "details": exc.detail if not isinstance(exc.detail, str) else None,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            f"Validation error: path={request.url.path}, errors={exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "message": "Validation Error",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(OperationalError)
    async def db_operational_error_handler(
        request: Request, exc: OperationalError
    ) -> JSONResponse:
        logger.error(
            f"Database connection / operational error on path={request.url.path}: {str(exc)}"
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": status.HTTP_503_SERVICE_UNAVAILABLE,
                    "message": "Database service is currently unavailable. Please check database connectivity.",
                    "details": None,
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_general_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error(
            f"Database query error on path={request.url.path}: {str(exc)}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Database query error occurred.",
                    "details": None,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            f"Unhandled server error on path={request.url.path}: {str(exc)}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Internal Server Error",
                    "details": None,
                }
            },
        )
