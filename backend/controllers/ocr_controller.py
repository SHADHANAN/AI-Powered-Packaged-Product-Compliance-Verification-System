from fastapi import UploadFile, HTTPException, status
from services.ocr_service.image_utils import validate_image_bytes, is_valid_extension
from services.ocr_service.ocr import get_ocr_service
from backend.schemas.ocr import OCRResponse, OCRLineResponse
from backend.utils.logger import logger


class OCRController:
    """
    Controller managing image upload validation and OCR processing.
    """

    @staticmethod
    async def process_image(
        file: UploadFile,
        strategy: str = "standard",
    ) -> OCRResponse:
        """
        Validates the uploaded package image and extracts structured text using OCR.
        """
        from services.ocr_service.image_utils import is_valid_mime_type, sanitize_filename
        # Validate MIME type if present
        if file.content_type and not is_valid_mime_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file MIME type '{file.content_type}'. Please upload a valid image (JPEG, PNG, WEBP, BMP, TIFF).",
            )

        clean_filename = sanitize_filename(file.filename) if file.filename else None

        # Validate filename & extension if available
        if clean_filename and not is_valid_extension(clean_filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{file.filename}'. Please upload a valid image (JPEG, PNG, WEBP, BMP, TIFF).",
            )

        # Read file contents
        try:
            image_bytes = await file.read()
        except Exception as e:
            logger.error(f"Failed to read uploaded file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not read uploaded file: {str(e)}",
            )

        # Validate image integrity and dimensions
        is_valid, error_msg, _ = validate_image_bytes(image_bytes, filename=file.filename)
        if not is_valid:
            logger.warning(f"Image validation failed for '{file.filename}': {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg or "Invalid image file provided.",
            )

        # Execute OCR
        ocr_service = get_ocr_service()
        ocr_result = ocr_service.extract_text(
            image_input=image_bytes,
            preprocess=True,
            strategy=strategy,
        )

        if not ocr_result.success:
            logger.error(f"OCR extraction failed: {ocr_result.error_message}")
            return OCRResponse(
                success=False,
                text="",
                lines=[],
                average_confidence=0.0,
                error_message=ocr_result.error_message,
                processing_time_ms=ocr_result.processing_time_ms,
            )

        return OCRResponse(
            success=True,
            text=ocr_result.text,
            lines=[
                OCRLineResponse(
                    text=line.text,
                    confidence=line.confidence,
                    bounding_box=line.bounding_box,
                )
                for line in ocr_result.lines
            ],
            average_confidence=ocr_result.average_confidence,
            processing_time_ms=ocr_result.processing_time_ms,
        )
