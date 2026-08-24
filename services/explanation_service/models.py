from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceItem:
    """
    Strict evidence item constructed from deterministic rule results and extracted fields.
    """
    rule_code: str
    rule_name: str
    status: str  # PASS, FAIL, WARN, NOT_APPLICABLE
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    source_field: Optional[str] = None
    rule_explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplanationContext:
    """
    Context package containing strictly verified evidence for the explanation generator.
    """
    overall_status: str
    overall_score: float
    product_name: Optional[str] = None
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    extracted_fields_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "overall_score": self.overall_score,
            "product_name": self.product_name,
            "evidence_items": [item.to_dict() for item in self.evidence_items],
            "extracted_fields_summary": self.extracted_fields_summary,
        }


@dataclass
class GeneratedExplanationItem:
    """
    Structured legal explanation and remediation guidance for a single rule check.
    """
    rule_code: str
    rule_name: str
    severity: str
    status: str
    explanation: str
    why_it_matters: str
    recommended_action: str
    evidence: str
    confidence: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplanationResult:
    """
    Complete explanation output including executive summary and remediation recommendations.
    """
    overall_status: str
    overall_score: float
    summary: str
    explanations: List[GeneratedExplanationItem] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    ai_generated: bool = False
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "overall_score": self.overall_score,
            "summary": self.summary,
            "explanations": [e.to_dict() for e in self.explanations],
            "recommendations": self.recommendations,
            "ai_generated": self.ai_generated,
            "error_message": self.error_message,
        }
