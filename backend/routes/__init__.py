from fastapi import APIRouter
from .health import router as health_router
from .products import router as products_router
from .verifications import router as verifications_router
from .ocr import router as ocr_router
from .extraction import router as extraction_router
from .compliance import router as compliance_router
from .explanation import router as explanation_router
from .verify import router as verify_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(products_router)
api_router.include_router(verifications_router)
api_router.include_router(ocr_router)
api_router.include_router(extraction_router)
api_router.include_router(compliance_router)
api_router.include_router(explanation_router)
api_router.include_router(verify_router)

__all__ = ["api_router"]
