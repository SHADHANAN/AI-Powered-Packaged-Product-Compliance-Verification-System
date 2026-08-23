from typing import Any, Dict, List, Optional, Union
from services.compliance_service.models import (
    RuleCheckResult,
    ComplianceEvaluationSummary,
)
from services.compliance_service.rules import load_all_rules
from services.compliance_service.validator import (
    validate_mandatory_field,
    validate_quantity_rules,
    validate_pricing_rules,
    validate_declaration_relationships,
)
from services.compliance_service.compliance_score import ComplianceScoreCalculator


class RuleEngine:
    """
    Deterministic Legal Metrology compliance rule evaluation engine.
    """

    def __init__(self, rules: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self._rules = rules or load_all_rules()

    @staticmethod
    def _normalize_fields_dict(
        extracted_fields: Union[Dict[str, Any], List[Dict[str, Any]], List[Any]]
    ) -> Dict[str, Any]:
        """
        Normalizes various representations of extracted fields into a standard dictionary.
        """
        if isinstance(extracted_fields, dict):
            return extracted_fields

        normalized: Dict[str, Any] = {}
        if isinstance(extracted_fields, list):
            for item in extracted_fields:
                if isinstance(item, dict) and "field_name" in item:
                    normalized[item["field_name"]] = item
                elif hasattr(item, "field_name"):
                    normalized[item.field_name] = item
        return normalized

    def evaluate(
        self,
        extracted_fields: Union[Dict[str, Any], List[Dict[str, Any]], List[Any]],
    ) -> ComplianceEvaluationSummary:
        """
        Evaluates extracted packaging declarations against configured Legal Metrology rules.
        """
        fields = self._normalize_fields_dict(extracted_fields)
        checks: List[RuleCheckResult] = []

        # 1. Mandatory Declarations
        mandatory_rules = self._rules.get("mandatory", [])
        for rule in mandatory_rules:
            if rule.get("enabled", True):
                checks.append(validate_mandatory_field(rule, fields))

        # 2. Quantity Rules
        qty_rules = self._rules.get("quantity", [])
        checks.extend(validate_quantity_rules(qty_rules, fields))

        # 3. Pricing Rules
        price_rules = self._rules.get("pricing", [])
        checks.extend(validate_pricing_rules(price_rules, fields))

        # 4. Declaration Relationships (Imported vs Domestic, Date sequences)
        decl_rules = self._rules.get("declarations", [])
        checks.extend(validate_declaration_relationships(decl_rules, fields))

        # 5. Calculate Score & Aggregate Status
        score, status, stats = ComplianceScoreCalculator.calculate(checks)

        return ComplianceEvaluationSummary(
            status=status,
            overall_score=score,
            checks=checks,
            total_rules_evaluated=stats["total_rules"],
            passed_count=stats["passed"],
            failed_count=stats["failed"],
            warning_count=stats["warnings"],
        )

    @classmethod
    def evaluate_fields(
        cls,
        extracted_fields: Union[Dict[str, Any], List[Dict[str, Any]], List[Any]],
    ) -> ComplianceEvaluationSummary:
        """
        Convenience class method to evaluate extracted fields using default rules.
        """
        engine = cls()
        return engine.evaluate(extracted_fields)
