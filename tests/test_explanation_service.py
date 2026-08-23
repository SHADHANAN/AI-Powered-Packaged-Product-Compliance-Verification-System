import pytest
from services.explanation_service import (
    EvidenceItem,
    ExplanationContext,
    build_evidence_context,
    get_deterministic_explanation,
    generate_deterministic_recommendations,
    generate_deterministic_result,
    LLMExplanationService,
    ExplanationReportGenerator,
)


def get_sample_evidence_items():
    return [
        EvidenceItem(
            rule_code="LM-MANDATORY-001",
            rule_name="Product / Commodity Name",
            status="PASS",
            severity="HIGH",
            expected_value="Commodity name must be clearly declared",
            actual_value="Potato Chips",
            rule_explanation="Product name is present.",
        ),
        EvidenceItem(
            rule_code="LM-MANDATORY-002",
            rule_name="Net Quantity Declaration",
            status="FAIL",
            severity="CRITICAL",
            expected_value="Net quantity must be declared with metric unit",
            actual_value="Missing",
            rule_explanation="Net quantity is missing from package labeling.",
        ),
        EvidenceItem(
            rule_code="LM-MANDATORY-003",
            rule_name="Maximum Retail Price (MRP)",
            status="FAIL",
            severity="CRITICAL",
            expected_value="MRP in INR must be declared",
            actual_value="Missing",
            rule_explanation="MRP declaration is missing.",
        ),
        EvidenceItem(
            rule_code="LM-QTY-002",
            rule_name="Standard Legal Metrology Unit",
            status="WARN",
            severity="HIGH",
            expected_value="Metric unit: g, kg, ml, l, pcs",
            actual_value="cups",
            rule_explanation="Unit 'cups' may not be standard metric.",
        ),
    ]


def test_evidence_construction():
    """Test building strict evidence context from raw check dictionaries."""
    checks = [
        {
            "rule_code": "LM-MANDATORY-001",
            "rule_name": "Product / Commodity Name",
            "status": "PASS",
            "severity": "HIGH",
            "expected_value": "Declared",
            "actual_value": "Potato Chips",
            "explanation": "Product name found.",
        }
    ]
    extracted = {"product_name": {"value": "Potato Chips"}}
    context = build_evidence_context(
        checks=checks,
        overall_score=100.0,
        overall_status="COMPLIANT",
        extracted_fields=extracted,
    )
    assert context.overall_score == 100.0
    assert context.overall_status == "COMPLIANT"
    assert len(context.evidence_items) == 1
    assert context.evidence_items[0].source_field == "product_name"


def test_deterministic_explanation_generation():
    """Test deterministic explanations and recommendations without LLM."""
    items = get_sample_evidence_items()
    context = ExplanationContext(
        overall_status="NON_COMPLIANT",
        overall_score=55.0,
        product_name="Potato Chips",
        evidence_items=items,
    )
    res = generate_deterministic_result(context)
    assert res.overall_status == "NON_COMPLIANT"
    assert res.overall_score == 55.0
    assert res.ai_generated is False
    assert len(res.explanations) == 4
    assert len(res.recommendations) >= 2

    # Check that failed rules have actionable advice
    mrp_exp = next(e for e in res.explanations if e.rule_code == "LM-MANDATORY-003")
    assert mrp_exp.status == "FAIL"
    assert "Maximum Retail Price" in mrp_exp.why_it_matters
    assert "Declare the Maximum Retail Price" in mrp_exp.recommended_action


def test_fully_compliant_product_report():
    """Test explanation report for a fully compliant product."""
    pass_items = [
        EvidenceItem(
            rule_code="LM-MANDATORY-001",
            rule_name="Product Name",
            status="PASS",
            severity="HIGH",
            expected_value="Declared",
            actual_value="Organic Honey",
        ),
        EvidenceItem(
            rule_code="LM-MANDATORY-003",
            rule_name="MRP",
            status="PASS",
            severity="CRITICAL",
            expected_value="Declared",
            actual_value="Rs. 150.00",
        ),
    ]
    context = ExplanationContext(
        overall_status="COMPLIANT",
        overall_score=100.0,
        product_name="Organic Honey",
        evidence_items=pass_items,
    )
    res = generate_deterministic_result(context)
    assert "COMPLIANT" in res.summary
    assert res.overall_score == 100.0
    assert len(res.recommendations) >= 1


def test_llm_service_mock_generation():
    """Test LLM service with default mock provider."""
    items = get_sample_evidence_items()
    context = ExplanationContext(
        overall_status="NON_COMPLIANT",
        overall_score=55.0,
        product_name="Potato Chips",
        evidence_items=items,
    )
    llm_service = LLMExplanationService(provider="mock")
    report = ExplanationReportGenerator.generate_report(context, llm_service=llm_service)

    assert report.ai_generated is True
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.explanations) == 4
    assert len(report.recommendations) >= 2


def test_llm_fallback_on_missing_key_or_failure():
    """Test that missing API key or invalid provider seamlessly falls back to deterministic rules."""
    items = get_sample_evidence_items()
    context = ExplanationContext(
        overall_status="NON_COMPLIANT",
        overall_score=55.0,
        product_name="Potato Chips",
        evidence_items=items,
    )
    # Gemini without API key -> should fallback
    llm_service = LLMExplanationService(provider="gemini", api_key="")
    report = ExplanationReportGenerator.generate_report(context, llm_service=llm_service)

    assert report.ai_generated is False  # Fallback engaged
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.explanations) == 4
    assert len(report.recommendations) >= 2


def test_llm_service_json_parsing_and_hallucination_prevention():
    """Test that LLM JSON parser filters unknown rule codes and preserves authoritative items."""
    service = LLMExplanationService(provider="mock")
    items = get_sample_evidence_items()
    context = ExplanationContext(
        overall_status="NON_COMPLIANT",
        overall_score=55.0,
        product_name="Potato Chips",
        evidence_items=items,
    )

    fake_json = """
    {
      "summary": "AI Summary",
      "explanations": [
        {
          "rule_code": "LM-MANDATORY-002",
          "rule_name": "Net Quantity Declaration",
          "severity": "CRITICAL",
          "status": "FAIL",
          "explanation": "Net quantity is missing from display panel.",
          "why_it_matters": "Consumer transparency",
          "recommended_action": "Add net quantity in grams",
          "evidence": "Missing",
          "confidence": 0.99
        },
        {
          "rule_code": "HALLUCINATED-CODE-999",
          "rule_name": "Fake Law",
          "severity": "LOW",
          "status": "FAIL",
          "explanation": "Invented rule",
          "why_it_matters": "None",
          "recommended_action": "None",
          "evidence": "Fake",
          "confidence": 0.5
        }
      ],
      "recommendations": ["Add net quantity in grams"]
    }
    """
    res = service._parse_llm_json_response(fake_json, context)
    assert res is not None
    assert res.ai_generated is True
    # Hallucinated rule code should be ignored, and original 4 evidence items preserved
    rule_codes = [e.rule_code for e in res.explanations]
    assert "HALLUCINATED-CODE-999" not in rule_codes
    assert "LM-MANDATORY-002" in rule_codes
    assert "LM-MANDATORY-001" in rule_codes
    assert len(res.explanations) == 4
