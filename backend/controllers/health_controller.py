from pydantic import BaseModel
from backend.config import get_settings


class HealthResponse(BaseModel):
    """
    Health check response model.
    """
    status: str
    service: str


class HealthController:
    """
    Controller handling system health verification.
    """

    @staticmethod
    def get_health() -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            status="healthy",
            service=settings.APP_NAME,
        )
