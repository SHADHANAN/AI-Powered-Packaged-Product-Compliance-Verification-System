from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ComplianceCheckBase(BaseModel):
    """
    Base schema for compliance checks.
    """
    rule_code: str = Field(..., max_length=100, description="Unique regulatory rule code")
    rule_name: str = Field(..., max_length=255, description="Human-readable rule name")
    status: str = Field(..., description="Evaluation status: pass, fail, warning, not_applicable")
    expected_value: Optional[str] = Field(None, description="Expected legal declaration/pattern")
    actual_value: Optional[str] = Field(None, description="Extracted actual declaration")
    explanation: Optional[str] = Field(None, description="Detailed compliance reasoning")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")


class ComplianceCheckCreate(ComplianceCheckBase):
    """
    Schema for creating a compliance check record.
    """
    verification_id: int


class ComplianceCheckResponse(ComplianceCheckBase):
    """
    Schema for returning a compliance check result.
    """
    id: int
    verification_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
