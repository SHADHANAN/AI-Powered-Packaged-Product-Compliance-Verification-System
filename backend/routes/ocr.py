from fastapi import APIRouter, File, Query, UploadFile, status
from backend.controllers.ocr_controller import OCRController
from backend.schemas.ocr import OCRResponse

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post(
    "",
    response_model=OCRResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from package image using OCR",
    description=(
        "Upload a packaged product or commodity label image to perform validation, "
        "modular preprocessing, and OCR text extraction. Returns structured bounding boxes, "
        "recognized lines, and confidence metrics."
    ),
)
async def process_ocr_image(
    file: UploadFile = File(
        ...,
        description="Product packaging image (JPEG, PNG, WEBP, BMP, TIFF)",
    ),
    strategy: str = Query(
        "standard",
        description="Preprocessing strategy: 'standard', 'grayscale_clahe', 'binarized', or 'raw'",
    ),
) -> OCRResponse:
    return await OCRController.process_image(file=file, strategy=strategy)
