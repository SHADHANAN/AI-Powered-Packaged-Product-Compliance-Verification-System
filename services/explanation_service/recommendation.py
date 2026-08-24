from typing import Dict, List
from services.explanation_service.models import (
    EvidenceItem,
    ExplanationContext,
    GeneratedExplanationItem,
    ExplanationResult,
)

# Rule metadata catalog containing deterministic legal rationales and remediation templates
RULE_RATIONALE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "LM-MANDATORY-001": {
        "why_it_matters": "The commodity name informs consumers of the exact identity and nature of the packaged product.",
        "pass_action": "Product/commodity identity declaration is compliant.",
        "fail_action": "Add a clearly visible and unambiguous product/commodity name to the principal display panel.",
        "pass_explanation": "Commodity name declaration is clearly present and compliant.",
        "fail_explanation": "The product identity or commodity name declaration is missing from the package label.",
    },
    "LM-MANDATORY-002": {
        "why_it_matters": "Net quantity declaration ensures consumer transparency regarding the true content volume or weight in metric units.",
        "pass_action": "Net quantity declaration is compliant.",
        "fail_action": "Declare the net quantity prominently together with an approved standard metric unit (e.g. g, kg, ml, l).",
        "pass_explanation": "Net quantity is declared with an approved metric unit.",
        "fail_explanation": "Net quantity declaration is missing or lacks standard metric unit designation.",
    },
    "LM-MANDATORY-003": {
        "why_it_matters": "Maximum Retail Price (MRP) protects consumers from overcharging and ensures all applicable taxes are included.",
        "pass_action": "Maximum Retail Price declaration is compliant.",
        "fail_action": "Declare the Maximum Retail Price in INR (e.g., 'MRP Rs. XX.XX' or 'MRP ₹ XX.XX (incl. of all taxes)').",
        "pass_explanation": "Maximum Retail Price (MRP) declaration is present and valid.",
        "fail_explanation": "The package lacks a valid Maximum Retail Price (MRP) declaration.",
    },
    "LM-MANDATORY-004": {
        "why_it_matters": "Manufacturer or packer identification provides accountability and manufacturer traceability.",
        "pass_action": "Manufacturer/packer identification is compliant.",
        "fail_action": "Add complete name and address of the manufacturer, packer, or marketer.",
        "pass_explanation": "Manufacturer or packer identity is clearly declared.",
        "fail_explanation": "Manufacturer or packer name and address is missing from packaging.",
    },
    "LM-MANDATORY-005": {
        "why_it_matters": "Manufacturing or packaging date allows consumers and regulators to determine product freshness and shelf-life.",
        "pass_action": "Date of manufacture/packaging is compliant.",
        "fail_action": "Declare the month and year of manufacture or packaging (e.g., 'MFD MM/YYYY').",
        "pass_explanation": "Date of manufacture/packaging is declared.",
        "fail_explanation": "Date of manufacture or packaging is missing from the label.",
    },
    "LM-MANDATORY-006": {
        "why_it_matters": "Batch or lot identification is critical for quality control, batch traceability, and product recall management.",
        "pass_action": "Batch/lot identification is compliant.",
        "fail_action": "Add a distinct batch number or lot identifier (e.g., 'Batch No: ...' or 'Lot: ...').",
        "pass_explanation": "Batch or lot identification code is present.",
        "fail_explanation": "Batch or lot identification number is missing.",
    },
    "LM-MANDATORY-007": {
        "why_it_matters": "Consumer care information ensures consumers can register complaints, inquiries, or feedback directly with the company.",
        "pass_action": "Consumer care details are compliant.",
        "fail_action": "Add valid consumer-care contact details (toll-free telephone number, email, or physical postal address).",
        "pass_explanation": "Consumer grievance redressal contact information is present.",
        "fail_explanation": "Consumer grievance redressal contact information (phone/email/address) is missing.",
    },
    "LM-MANDATORY-008": {
        "why_it_matters": "Country of origin declaration is mandatory for transparency and import compliance.",
        "pass_action": "Country of origin declaration is compliant.",
        "fail_action": "Declare the country of origin clearly (e.g., 'Made in India' or 'Country of Origin: ...').",
        "pass_explanation": "Country of origin declaration is present.",
        "fail_explanation": "Country of origin declaration is missing from the package label.",
    },
    "LM-QTY-001": {
        "why_it_matters": "Net quantity magnitude must be greater than zero to represent a genuine commercial quantity.",
        "pass_action": "Quantity magnitude is positive and valid.",
        "fail_action": "Correct the net quantity so that it represents a positive numerical value strictly greater than zero.",
        "pass_explanation": "Quantity magnitude is greater than zero.",
        "fail_explanation": "Net quantity value must be strictly greater than zero.",
    },
    "LM-QTY-002": {
        "why_it_matters": "Standard metric measurement units are required by Legal Metrology rules to prevent consumer confusion.",
        "pass_action": "Measurement unit conforms to Legal Metrology standards.",
        "fail_action": "Use an approved standard metric unit: 'g', 'kg', 'mg', 'ml', 'l', or 'pcs'.",
        "pass_explanation": "Declared unit is an approved Legal Metrology metric unit.",
        "fail_explanation": "Measurement unit is non-standard or missing.",
    },
    "LM-PRICE-001": {
        "why_it_matters": "MRP must be a valid positive numerical monetary figure.",
        "pass_action": "MRP format and value are valid.",
        "fail_action": "Correct the MRP so that it is a positive numeric amount in Indian Rupees.",
        "pass_explanation": "MRP is a valid positive amount in INR.",
        "fail_explanation": "MRP must be a positive numeric amount greater than zero.",
    },
    "LM-DECL-001": {
        "why_it_matters": "Imported commodities require explicit importer registration and origin details under Legal Metrology Import Rules.",
        "pass_action": "Import declaration requirements are satisfied.",
        "fail_action": "For imported products, declare the name and complete address of the importer together with country of origin.",
        "pass_explanation": "Import declarations are properly declared.",
        "fail_explanation": "Product is of foreign origin but lacks mandatory importer details.",
    },
    "LM-DECL-002": {
        "why_it_matters": "Logical chronological ordering between manufacture and expiry prevents selling expired goods.",
        "pass_action": "Date sequence is chronologically consistent.",
        "fail_action": "Correct the manufacturing and expiry dates so that the expiry/best-before date does not precede manufacture date.",
        "pass_explanation": "Date sequence between manufacture and expiry is chronologically valid.",
        "fail_explanation": "Expiry date precedes the declared date of manufacture.",
    },
}


def get_deterministic_explanation(item: EvidenceItem) -> GeneratedExplanationItem:
    """
    Generates a deterministic explanation item using the template catalog.
    """
    meta = RULE_RATIONALE_TEMPLATES.get(item.rule_code, {})
    is_pass = item.status.upper() in {"PASS", "NOT_APPLICABLE"}

    why_it_matters = meta.get(
        "why_it_matters",
        f"Compliance with {item.rule_name} is required under Legal Metrology regulations."
    )

    if is_pass:
        recommended_action = meta.get("pass_action", f"{item.rule_name} satisfies compliance standards.")
        explanation = item.rule_explanation or meta.get("pass_explanation", f"{item.rule_name} is compliant.")
    else:
        recommended_action = meta.get("fail_action", f"Ensure {item.rule_name} is accurately and clearly declared.")
        explanation = item.rule_explanation or meta.get("fail_explanation", f"{item.rule_name} failed compliance check.")

    evidence_str = (
        f"Expected: '{item.expected_value or 'Declared'}' | "
        f"Actual: '{item.actual_value or 'Missing'}'"
    )

    return GeneratedExplanationItem(
        rule_code=item.rule_code,
        rule_name=item.rule_name,
        severity=item.severity,
        status=item.status,
        explanation=explanation,
        why_it_matters=why_it_matters,
        recommended_action=recommended_action,
        evidence=evidence_str,
        confidence=0.98,
    )


def generate_deterministic_recommendations(items: List[EvidenceItem]) -> List[str]:
    """
    Extracts high-priority deduplicated remediation recommendations from failed/warning checks.
    """
    recommendations: List[str] = []
    seen = set()

    for item in items:
        if item.status.upper() in {"FAIL", "WARN"}:
            meta = RULE_RATIONALE_TEMPLATES.get(item.rule_code, {})
            rec = meta.get("fail_action", f"Correct {item.rule_name} declaration to meet compliance standards.")
            if rec not in seen:
                seen.add(rec)
                recommendations.append(rec)

    if not recommendations:
        recommendations.append("Package satisfies all evaluated Legal Metrology declaration standards.")

    return recommendations


def generate_deterministic_summary(context: ExplanationContext) -> str:
    """
    Generates an executive summary based on overall status, score, and failed rules.
    """
    failed_items = [item for item in context.evidence_items if item.status.upper() == "FAIL"]
    warn_items = [item for item in context.evidence_items if item.status.upper() == "WARN"]

    if context.overall_status.upper() == "COMPLIANT" or (len(failed_items) == 0 and len(warn_items) == 0):
        return (
            f"The package achieved an overall compliance score of {context.overall_score:.1f}/100 "
            f"and is fully COMPLIANT with evaluated Legal Metrology (Packaged Commodities) requirements."
        )
    elif context.overall_status.upper() == "PARTIALLY_COMPLIANT":
        failed_names = ", ".join([f.rule_name for f in failed_items[:3]])
        return (
            f"The package achieved a score of {context.overall_score:.1f}/100 and is PARTIALLY COMPLIANT. "
            f"Key areas requiring rectification include: {failed_names}."
        )
    else:
        failed_names = ", ".join([f.rule_name for f in failed_items[:4]])
        return (
            f"The package is NON_COMPLIANT with an overall score of {context.overall_score:.1f}/100. "
            f"Critical non-compliances were identified in: {failed_names}."
        )


def generate_deterministic_result(context: ExplanationContext) -> ExplanationResult:
    """
    Builds a complete, deterministic explanation result.
    """
    explanations = [get_deterministic_explanation(item) for item in context.evidence_items]
    recommendations = generate_deterministic_recommendations(context.evidence_items)
    summary = generate_deterministic_summary(context)

    return ExplanationResult(
        overall_status=context.overall_status,
        overall_score=context.overall_score,
        summary=summary,
        explanations=explanations,
        recommendations=recommendations,
        ai_generated=False,
        error_message=None,
    )
