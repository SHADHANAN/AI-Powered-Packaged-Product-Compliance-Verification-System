from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExplanationItem(BaseModel):
    """
    Detailed explanation and remediation advice for an individual compliance rule check.
    """
    rule_code: str = Field(..., description="Regulatory rule code (e.g. LM-MANDATORY-001)")
    rule_name: str = Field(..., description="Human-readable rule name")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    status: str = Field(..., description="Rule evaluation status: PASS, FAIL, WARN, NOT_APPLICABLE")
    explanation: str = Field(..., description="Human-readable explanation of why the rule passed or failed")
    why_it_matters: str = Field(..., description="Regulatory and consumer rationale for the requirement")
    recommended_action: str = Field(..., description="Concrete corrective action to achieve full compliance")
    evidence: str = Field(..., description="Grounding evidence from label extraction (actual vs expected)")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Confidence of the generated explanation")

    model_config = ConfigDict(from_attributes=True)


class ExplanationRequest(BaseModel):
    """
    Request payload to generate legal explanations and remediation recommendations.
    Accepts either an existing verification_id or a direct list of evaluated checks.
    """
    verification_id: Optional[int] = Field(
        None,
        description="ID of existing Verification record to load checks and evidence from",
        examples=[1],
    )
    checks: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Direct list of compliance check items (e.g. from Phase 5 RuleEngine)",
    )
    overall_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Overall compliance score if evaluating directly",
    )
    status: Optional[str] = Field(
        None,
        description="Overall compliance status if evaluating directly (COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT)",
    )

    @model_validator(mode="after")
    def validate_request_source(self):
        if self.verification_id is None and (not self.checks or len(self.checks) == 0):
            raise ValueError("Either verification_id or non-empty checks list must be provided.")
        return self


class ExplanationResponse(BaseModel):
    """
    Structured outcome of AI-powered legal explanations and remediation recommendations.
    """
    success: bool = Field(..., description="Whether explanation generation succeeded")
    verification_id: Optional[int] = Field(None, description="Associated Verification ID if loaded from DB")
    overall_status: str = Field(..., description="Authoritative compliance status from Phase 5")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Authoritative overall compliance score")
    summary: str = Field(..., description="Overall executive summary of compliance findings")
    explanations: List[ExplanationItem] = Field(default_factory=list, description="Per-rule explanations and guidance")
    recommendations: List[str] = Field(default_factory=list, description="Consolidated actionable remediation recommendations")
    ai_generated: bool = Field(default=False, description="True if generated via LLM, False if produced via deterministic fallback")
    error_message: Optional[str] = Field(None, description="Error message if LLM failed and fallback was engaged")

    model_config = ConfigDict(from_attributes=True)
