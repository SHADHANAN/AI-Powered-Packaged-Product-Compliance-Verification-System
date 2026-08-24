from typing import Dict, List, Optional, Tuple
from services.compliance_service.models import RuleCheckResult

# Default penalty deductions per failed rule by severity
SEVERITY_DEDUCTIONS: Dict[str, float] = {
    "CRITICAL": 25.0,
    "HIGH": 20.0,
    "MEDIUM": 10.0,
    "LOW": 5.0,
}

# Status score thresholds
COMPLIANT_THRESHOLD = 90.0
PARTIALLY_COMPLIANT_THRESHOLD = 70.0


class ComplianceScoreCalculator:
    """
    Deterministic scoring calculator evaluating aggregate rule compliance.
    """

    @classmethod
    def calculate(
        cls,
        checks: List[RuleCheckResult],
        initial_score: float = 100.0,
        deductions: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, str, Dict[str, int]]:
        """
        Computes the overall score, compliance status, and check statistics.
        Returns: (overall_score, status, stats_dict)
        """
        penalty_weights = deductions or SEVERITY_DEDUCTIONS
        score = initial_score

        passed_count = 0
        failed_count = 0
        warning_count = 0

        for check in checks:
            status_upper = check.status.upper()
            severity_upper = check.severity.upper()
            penalty = penalty_weights.get(severity_upper, 10.0)

            if status_upper == "PASS":
                passed_count += 1
            elif status_upper == "FAIL":
                failed_count += 1
                score -= penalty
            elif status_upper == "WARN":
                warning_count += 1
                score -= (penalty * 0.5)
            elif status_upper == "NOT_APPLICABLE":
                pass

        # Clamp between 0.0 and 100.0
        final_score = max(0.0, min(100.0, score))

        if final_score >= COMPLIANT_THRESHOLD and failed_count == 0:
            status = "COMPLIANT"
        elif final_score >= PARTIALLY_COMPLIANT_THRESHOLD:
            status = "PARTIALLY_COMPLIANT"
        else:
            status = "NON_COMPLIANT"

        stats = {
            "total_rules": len(checks),
            "passed": passed_count,
            "failed": failed_count,
            "warnings": warning_count,
        }

        return round(final_score, 2), status, stats
