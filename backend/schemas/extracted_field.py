from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractedFieldBase(BaseModel):
    """
    Base schema for extracted packaging fields.
    """
    field_name: str = Field(..., max_length=100, description="Name of the extracted attribute")
    field_value: Optional[str] = Field(None, description="Extracted text value")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Extraction confidence score")
    source_text: Optional[str] = Field(None, description="Raw source text line/bounding-box text")


class ExtractedFieldCreate(ExtractedFieldBase):
    """
    Schema for creating an extracted field record.
    """
    verification_id: int


class ExtractedFieldResponse(ExtractedFieldBase):
    """
    Schema for returning an extracted field record.
    """
    id: int
    verification_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
