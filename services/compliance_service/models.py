from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class RuleCheckResult:
    """
    Result of evaluating an individual Legal Metrology rule against extracted packaging data.
    """
    rule_code: str
    rule_name: str
    status: str  # PASS, FAIL, WARN, NOT_APPLICABLE
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ComplianceEvaluationSummary:
    """
    Aggregate summary of all compliance checks and overall score.
    """
    status: str  # COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT
    overall_score: float
    checks: List[RuleCheckResult] = field(default_factory=list)
    total_rules_evaluated: int = 0
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "overall_score": round(self.overall_score, 2),
            "checks": [c.to_dict() for c in self.checks],
            "total_rules_evaluated": self.total_rules_evaluated,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "warning_count": self.warning_count,
        }
