from fastapi import HTTPException, status
from services.extraction_service.extractor import extract_product_fields
from backend.schemas.extraction import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionFieldItem,
)
from backend.utils.logger import logger


class ExtractionController:
    """
    Controller handling NLP field extraction and normalization from raw OCR text.
    """

    @staticmethod
    def extract_fields(request: ExtractionRequest) -> ExtractionResponse:
        """
        Executes deterministic regex and NLP field extraction on raw OCR text.
        """
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OCR text payload cannot be empty.",
            )

        try:
            result = extract_product_fields(request.text)

            field_items = [
                ExtractionFieldItem(
                    field_name=f.field_name,
                    value=f.value,
                    unit=f.unit,
                    raw_value=f.raw_value,
                    source_text=f.source_text,
                    confidence=f.confidence,
                )
                for f in result.fields
            ]

            return ExtractionResponse(
                success=result.success,
                fields=field_items,
                field_count=result.field_count,
                average_confidence=result.average_confidence,
                raw_text=result.raw_text,
            )

        except Exception as e:
            logger.exception(f"Field extraction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error occurred during field extraction: {str(e)}",
            )
