from typing import Any, Dict, List, Optional, Union
from services.explanation_service.models import EvidenceItem, ExplanationContext

# Map rule codes to their underlying extracted field identifiers
RULE_SOURCE_FIELDS: Dict[str, str] = {
    "LM-MANDATORY-001": "product_name",
    "LM-MANDATORY-002": "net_quantity",
    "LM-MANDATORY-003": "mrp",
    "LM-MANDATORY-004": "manufacturer_name",
    "LM-MANDATORY-005": "date_of_manufacture",
    "LM-MANDATORY-006": "batch_number",
    "LM-MANDATORY-007": "customer_care_details",
    "LM-MANDATORY-008": "country_of_origin",
    "LM-QTY-001": "net_quantity",
    "LM-QTY-002": "unit",
    "LM-PRICE-001": "mrp",
    "LM-DECL-001": "importer_name",
    "LM-DECL-002": "expiry_date",
}


def build_evidence_context(
    checks: List[Any],
    overall_score: float,
    overall_status: str,
    extracted_fields: Optional[Union[Dict[str, Any], List[Any]]] = None,
    product_name: Optional[str] = None,
) -> ExplanationContext:
    """
    Builds a strict, ground-truth evidence context from deterministic compliance checks
    and extracted product fields.
    """
    evidence_items: List[EvidenceItem] = []

    # Normalize extracted fields summary
    fields_summary: Dict[str, Any] = {}
    if extracted_fields:
        if isinstance(extracted_fields, dict):
            for k, v in extracted_fields.items():
                val = v.get("value") if isinstance(v, dict) else (getattr(v, "field_value", None) or getattr(v, "value", v))
                fields_summary[k] = str(val) if val is not None else None
        elif isinstance(extracted_fields, list):
            for item in extracted_fields:
                if isinstance(item, dict):
                    fname = item.get("field_name")
                    fval = item.get("value") or item.get("field_value")
                    if fname:
                        fields_summary[fname] = str(fval) if fval is not None else None
                elif hasattr(item, "field_name"):
                    fname = item.field_name
                    fval = getattr(item, "field_value", None) or getattr(item, "value", None)
                    if fname:
                        fields_summary[fname] = str(fval) if fval is not None else None

    # Determine product name if not explicitly passed
    p_name = product_name or fields_summary.get("product_name")

    for chk in checks:
        if isinstance(chk, dict):
            rule_code = chk.get("rule_code", "")
            rule_name = chk.get("rule_name", "")
            status = str(chk.get("status", "")).upper()
            severity = str(chk.get("severity", "MEDIUM")).upper()
            expected_val = chk.get("expected_value")
            actual_val = chk.get("actual_value")
            explanation = chk.get("explanation")
        else:
            rule_code = getattr(chk, "rule_code", "")
            rule_name = getattr(chk, "rule_name", "")
            status = str(getattr(chk, "status", "")).upper()
            severity = str(getattr(chk, "severity", "MEDIUM")).upper()
            expected_val = getattr(chk, "expected_value", None)
            actual_val = getattr(chk, "actual_value", None)
            explanation = getattr(chk, "explanation", None)

        source_field = RULE_SOURCE_FIELDS.get(rule_code)

        evidence_items.append(
            EvidenceItem(
                rule_code=rule_code,
                rule_name=rule_name,
                status=status,
                severity=severity,
                expected_value=expected_val,
                actual_value=actual_val,
                source_field=source_field,
                rule_explanation=explanation,
            )
        )

    return ExplanationContext(
        overall_status=overall_status,
        overall_score=overall_score,
        product_name=p_name,
        evidence_items=evidence_items,
        extracted_fields_summary=fields_summary,
    )
