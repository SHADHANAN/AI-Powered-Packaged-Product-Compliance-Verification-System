from datetime import datetime
from typing import List, Optional, Dict, Any
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


class VerificationListItem(VerificationResponse):
    """
    Verification record with associated product metadata for history listing.
    """
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)


class VerificationListResponse(BaseModel):
    """
    Paginated list of past verification records.
    """
    items: List[VerificationListItem]
    total: int
    skip: int
    limit: int


class VerificationDetailResponse(VerificationResponse):
    """
    Detailed verification response including product, extracted fields, and compliance checks.
    """
    product: Optional[ProductResponse] = None
    extracted_fields: List[ExtractedFieldResponse] = []
    compliance_checks: List[ComplianceCheckResponse] = []

    model_config = ConfigDict(from_attributes=True)


class VerificationReportResponse(BaseModel):
    """
    Comprehensive compliance audit report payload for a verification session.
    """
    verification_id: int
    product_id: int
    product_name: str
    brand_name: Optional[str] = None
    overall_status: str
    overall_score: float
    verified_at: Optional[datetime] = None
    summary: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    extracted_fields: List[Dict[str, Any]]
    compliance_checks: List[Dict[str, Any]]
    recommendations: List[str]
    markdown_report: str
