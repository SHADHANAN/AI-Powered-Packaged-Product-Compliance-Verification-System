from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ComplianceCheckBase(BaseModel):
    """
    Base schema for compliance checks.
    """
    rule_code: str = Field(..., max_length=100, description="Unique regulatory rule code")
    rule_name: str = Field(..., max_length=255, description="Human-readable rule name")
    status: str = Field(..., description="Evaluation status: PASS, FAIL, WARN, NOT_APPLICABLE")
    expected_value: Optional[str] = Field(None, description="Expected legal declaration/pattern")
    actual_value: Optional[str] = Field(None, description="Extracted actual declaration")
    explanation: Optional[str] = Field(None, description="Detailed compliance reasoning")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")


class ComplianceCheckCreate(ComplianceCheckBase):
    """
    Schema for creating a compliance check record in the database.
    """
    verification_id: int


class ComplianceCheckResponse(ComplianceCheckBase):
    """
    Schema for returning a compliance check result.
    """
    id: Optional[int] = None
    verification_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ComplianceEvaluationRequest(BaseModel):
    """
    Request schema for compliance evaluation endpoint.
    Accepts either an existing verification_id or a list/dict of extracted fields.
    """
    verification_id: Optional[int] = Field(
        None,
        description="ID of the Verification record to evaluate and persist results to",
        examples=[1],
    )
    extracted_fields: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional list of extracted field objects (e.g. from Phase 4)",
    )

    @model_validator(mode="after")
    def validate_input(self):
        if self.verification_id is None and not self.extracted_fields:
            raise ValueError("Either verification_id or extracted_fields must be provided.")
        return self


class ComplianceEvaluationResponse(BaseModel):
    """
    Structured outcome of the compliance evaluation.
    """
    success: bool = Field(..., description="Whether compliance evaluation succeeded")
    verification_id: Optional[int] = Field(None, description="Associated Verification ID if persisted")
    status: str = Field(..., description="Overall status: COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Computed compliance score (0-100)")
    checks: List[ComplianceCheckResponse] = Field(default_factory=list, description="Individual rule evaluation results")
    total_rules_evaluated: int = Field(default=0, description="Total number of rules checked")
    passed_count: int = Field(default=0, description="Number of passed rules")
    failed_count: int = Field(default=0, description="Number of failed rules")
    warning_count: int = Field(default=0, description="Number of warnings")

    model_config = ConfigDict(from_attributes=True)
