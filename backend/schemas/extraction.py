from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractionRequest(BaseModel):
    """
    Request payload containing raw OCR text for field extraction.
    """
    text: str = Field(
        ...,
        min_length=1,
        description="Raw OCR text extracted from packaged commodity labeling",
        examples=[
            "LAY'S\nChile Limón\nFlavour\nPROPRIETARY FOOD - POTATO CHIPS\nNET QTY 50 g\nMRP Rs. 20.00\nMFD 12/05/2024\nUSE BY 11/11/2024\nBATCH NO. 24E1205\nMFD. & MKTG. BY: PepsiCo India Holdings Pvt. Ltd.\nMADE IN INDIA\nCUSTOMER CARE: 1800 22 4020, consumer.feedback@pepsico.com"
        ],
    )


class ExtractionFieldItem(BaseModel):
    """
    Structured extraction of a single Legal Metrology / product attribute.
    """
    field_name: str = Field(..., description="Canonical name of the extracted field")
    value: Optional[Any] = Field(None, description="Normalized field value (number, string, etc.)")
    unit: Optional[str] = Field(None, description="Measurement unit if applicable (e.g., 'g', 'kg', 'ml', 'l')")
    raw_value: Optional[str] = Field(None, description="Raw string match from text")
    source_text: Optional[str] = Field(None, description="Original OCR source line for audit traceability")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score (0.0 - 1.0)")

    model_config = ConfigDict(from_attributes=True)


class ExtractionResponse(BaseModel):
    """
    Structured response containing all normalized fields and confidence metrics.
    """
    success: bool = Field(..., description="Whether field extraction succeeded")
    fields: List[ExtractionFieldItem] = Field(default_factory=list, description="Extracted product fields")
    field_count: int = Field(default=0, description="Total number of fields extracted")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average confidence score across all fields")
    raw_text: Optional[str] = Field(None, description="Input raw text that was processed")

    model_config = ConfigDict(from_attributes=True)
