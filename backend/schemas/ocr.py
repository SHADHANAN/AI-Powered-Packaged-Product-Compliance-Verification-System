from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class OCRLineResponse(BaseModel):
    """
    Schema for a single OCR detected text line.
    """
    text: str = Field(..., description="Recognized line text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    bounding_box: Optional[List[List[float]]] = Field(
        None, description="Polygon bounding box coordinates [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]"
    )

    model_config = ConfigDict(from_attributes=True)


class OCRResponse(BaseModel):
    """
    Schema for OCR endpoint response.
    """
    success: bool = Field(..., description="Whether OCR processing succeeded")
    text: str = Field(default="", description="Consolidated full text from all detected lines")
    lines: List[OCRLineResponse] = Field(default_factory=list, description="List of recognized lines")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average OCR confidence across all lines")
    error_message: Optional[str] = Field(None, description="Error details if processing failed")
    processing_time_ms: Optional[float] = Field(None, description="Processing duration in milliseconds")

    model_config = ConfigDict(from_attributes=True)
