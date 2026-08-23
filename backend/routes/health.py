from fastapi import APIRouter
from backend.controllers.health_controller import HealthController, HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns the operational status and service identifier of the backend.",
)
async def get_health() -> HealthResponse:
    """
    Health check endpoint returning service status.
    """
    return HealthController.get_health()
