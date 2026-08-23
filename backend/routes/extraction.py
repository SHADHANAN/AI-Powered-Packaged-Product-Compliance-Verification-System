from fastapi import APIRouter, status
from backend.controllers.extraction_controller import ExtractionController
from backend.schemas.extraction import ExtractionRequest, ExtractionResponse

router = APIRouter(prefix="/extract", tags=["Extraction"])


@router.post(
    "",
    response_model=ExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract structured product fields from OCR text",
    description=(
        "Extracts and normalizes Legal Metrology declarations, product identity, "
        "manufacturer details, pricing, net quantity, batch, and dates from raw OCR text. "
        "Preserves source traceability and provides extraction confidence scores."
    ),
)
async def extract_fields_from_ocr(request: ExtractionRequest) -> ExtractionResponse:
    return ExtractionController.extract_fields(request=request)
