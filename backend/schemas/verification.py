from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.schemas.product import ProductResponse
from backend.schemas.extracted_field import ExtractedFieldResponse
from backend.schemas.compliance import ComplianceCheckResponse


class VerificationBase(BaseModel):
    """
    Base schema for verification records.
    """
    product_id: int = Field(..., description="Referenced product ID")
    verification_status: str = Field(
        default="pending",
        description="Status: pending, processing, compliant, non_compliant, error"
    )
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Overall compliance score (0-100)")
    source_image_path: Optional[str] = Field(None, max_length=500, description="Path to source packaging image")


class VerificationCreate(VerificationBase):
    """
    Schema for creating a verification record.
    """
    pass


class VerificationResponse(VerificationBase):
    """
    Schema for basic verification responses.
    """
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VerificationDetailResponse(VerificationResponse):
    """
    Detailed verification response including product, extracted fields, and compliance checks.
    """
    product: Optional[ProductResponse] = None
    extracted_fields: List[ExtractedFieldResponse] = []
    compliance_checks: List[ComplianceCheckResponse] = []

    model_config = ConfigDict(from_attributes=True)
