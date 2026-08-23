from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PipelineOCRSummary(BaseModel):
    """OCR stage summary output."""
    text: str = Field(..., description="Recognized full text")
    average_confidence: float = Field(..., description="Average OCR detection confidence")
    line_count: int = Field(default=0, description="Total recognized text lines")


class PipelineExtractedFieldItem(BaseModel):
    """Normalized packaging declaration item."""
    field_name: str
    field_value: Optional[str] = None
    unit: Optional[str] = None
    confidence: float
    source_text: Optional[str] = None


class PipelineComplianceCheckItem(BaseModel):
    """Evaluated regulatory compliance check item."""
    rule_code: str
    rule_name: str
    status: str
    severity: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    explanation: Optional[str] = None


class PipelineExplanationItem(BaseModel):
    """Detailed legal explanation and remediation advice item."""
    rule_code: str
    rule_name: str
    severity: str
    status: str
    explanation: str
    why_it_matters: str
    recommended_action: str
    evidence: str
    confidence: float = 0.95


class PipelineExplanationSummary(BaseModel):
    """Explanation and remediation recommendations block."""
    summary: str
    items: List[PipelineExplanationItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    ai_generated: bool = False


class VerificationPipelineResponse(BaseModel):
    """
    Consolidated response for the end-to-end verification pipeline (POST /api/verify).
    """
    success: bool = Field(..., description="Whether the verification pipeline executed successfully")
    verification_id: Optional[int] = Field(None, description="Created Verification record ID in database")
    product_id: Optional[int] = Field(None, description="Created/Updated Product record ID in database")
    overall_status: str = Field(..., description="Authoritative compliance status (COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT)")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Authoritative overall compliance score (0-100)")
    ocr: Optional[PipelineOCRSummary] = Field(None, description="OCR text recognition summary")
    extracted_fields: List[PipelineExtractedFieldItem] = Field(default_factory=list, description="Extracted product declarations")
    compliance_checks: List[PipelineComplianceCheckItem] = Field(default_factory=list, description="Evaluated compliance checks")
    explanation: Optional[PipelineExplanationSummary] = Field(None, description="AI-generated legal explanations and recommendations")
    error_message: Optional[str] = Field(None, description="Error message if any pipeline stage encountered a critical error")

    model_config = ConfigDict(from_attributes=True)
