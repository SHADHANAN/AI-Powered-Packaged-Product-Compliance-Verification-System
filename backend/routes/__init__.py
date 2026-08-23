from fastapi import APIRouter
from .health import router as health_router
from .products import router as products_router
from .verifications import router as verifications_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(products_router)
api_router.include_router(verifications_router)

__all__ = ["api_router"]
