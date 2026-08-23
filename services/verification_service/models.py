from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class PipelineStageStatus:
    """Tracks execution status of individual verification pipeline stages."""
    image_validation: bool = False
    ocr: bool = False
    extraction: bool = False
    database_persist: bool = False
    compliance_evaluation: bool = False
    explanation_generation: bool = False


@dataclass
class VerificationPipelineResult:
    """
    Complete consolidated result of the end-to-end packaged product verification pipeline.
    """
    success: bool
    verification_id: Optional[int] = None
    product_id: Optional[int] = None
    overall_status: str = "PENDING"
    overall_score: float = 0.0
    ocr: Dict[str, Any] = field(default_factory=dict)
    extracted_fields: List[Dict[str, Any]] = field(default_factory=list)
    compliance_checks: List[Dict[str, Any]] = field(default_factory=list)
    explanation: Dict[str, Any] = field(default_factory=dict)
    stages: PipelineStageStatus = field(default_factory=PipelineStageStatus)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "verification_id": self.verification_id,
            "product_id": self.product_id,
            "overall_status": self.overall_status,
            "overall_score": round(self.overall_score, 2),
            "ocr": self.ocr,
            "extracted_fields": self.extracted_fields,
            "compliance_checks": self.compliance_checks,
            "explanation": self.explanation,
            "error_message": self.error_message,
        }
