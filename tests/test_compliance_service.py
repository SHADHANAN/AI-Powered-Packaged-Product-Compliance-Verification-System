import pytest
from services.compliance_service import (
    RuleEngine,
    ComplianceScoreCalculator,
    RuleCheckResult,
    ComplianceEvaluationSummary,
)
from services.compliance_service.validator import (
    validate_quantity_rules,
    validate_pricing_rules,
    validate_declaration_relationships,
)


def get_sample_compliant_fields():
    return {
        "product_name": "Potato Chips - Chile Limon",
        "brand_name": "LAY'S",
        "net_quantity": {"value": 50, "unit": "g"},
        "unit": "g",
        "mrp": 20.0,
        "date_of_manufacture": "12/05/2024",
        "expiry_date": "11/11/2024",
        "batch_number": "24E1205",
        "country_of_origin": "India",
        "manufacturer_name": "PepsiCo India Holdings Pvt. Ltd.",
        "customer_care_details": "1800 22 4020, feedback@pepsico.com",
    }


def test_fully_compliant_product():
    """Test evaluation of a complete and compliant product."""
    fields = get_sample_compliant_fields()
    engine = RuleEngine()
    summary: ComplianceEvaluationSummary = engine.evaluate(fields)

    assert summary.status == "COMPLIANT"
    assert summary.overall_score == 100.0
    assert summary.failed_count == 0
    assert summary.passed_count >= 8

    # Verify individual rule passes
    check_dict = {c.rule_code: c for c in summary.checks}
    assert check_dict["LM-MANDATORY-001"].status == "PASS"  # Product Name
    assert check_dict["LM-MANDATORY-002"].status == "PASS"  # Net Qty
    assert check_dict["LM-MANDATORY-003"].status == "PASS"  # MRP
    assert check_dict["LM-MANDATORY-004"].status == "PASS"  # Manufacturer
    assert check_dict["LM-QTY-001"].status == "PASS"        # Qty > 0
    assert check_dict["LM-QTY-002"].status == "PASS"        # Standard Unit
    assert check_dict["LM-PRICE-001"].status == "PASS"      # Valid MRP


def test_missing_product_name():
    """Test rule failure when product name is missing."""
    fields = get_sample_compliant_fields()
    del fields["product_name"]

    summary = RuleEngine.evaluate_fields(fields)
    check_dict = {c.rule_code: c for c in summary.checks}

    assert check_dict["LM-MANDATORY-001"].status == "FAIL"
    assert "missing" in check_dict["LM-MANDATORY-001"].explanation.lower()
    assert summary.overall_score <= 80.0


def test_missing_and_invalid_mrp():
    """Test failure on missing MRP and non-positive MRP."""
    # 1. Missing MRP
    fields_missing = get_sample_compliant_fields()
    del fields_missing["mrp"]
    summary_missing = RuleEngine.evaluate_fields(fields_missing)
    assert summary_missing.overall_score <= 60.0  # Fails MANDATORY-003 and PRICE-001

    # 2. Negative/Zero MRP
    fields_zero = get_sample_compliant_fields()
    fields_zero["mrp"] = 0.0
    summary_zero = RuleEngine.evaluate_fields(fields_zero)
    check_dict = {c.rule_code: c for c in summary_zero.checks}
    assert check_dict["LM-PRICE-001"].status == "FAIL"
    assert "greater than zero" in check_dict["LM-PRICE-001"].explanation.lower()


def test_quantity_and_unit_failures():
    """Test quantity magnitude and unit rule validations."""
    # Missing unit
    fields_no_unit = get_sample_compliant_fields()
    fields_no_unit["net_quantity"] = {"value": 50, "unit": None}
    fields_no_unit["unit"] = None

    summary_no_unit = RuleEngine.evaluate_fields(fields_no_unit)
    check_dict = {c.rule_code: c for c in summary_no_unit.checks}
    assert check_dict["LM-QTY-002"].status == "FAIL"

    # Zero Quantity
    fields_zero_qty = get_sample_compliant_fields()
    fields_zero_qty["net_quantity"] = {"value": 0, "unit": "g"}
    summary_zero_qty = RuleEngine.evaluate_fields(fields_zero_qty)
    check_dict_z = {c.rule_code: c for c in summary_zero_qty.checks}
    assert check_dict_z["LM-QTY-001"].status == "FAIL"


def test_imported_product_compliance():
    """Test imported product requires country of origin and importer."""
    # Foreign product without importer
    fields_foreign = get_sample_compliant_fields()
    fields_foreign["country_of_origin"] = "Germany"
    fields_foreign["importer_name"] = None

    summary = RuleEngine.evaluate_fields(fields_foreign)
    check_dict = {c.rule_code: c for c in summary.checks}
    assert check_dict["LM-DECL-001"].status == "FAIL"
    assert "foreign origin but lacks mandatory importer" in check_dict["LM-DECL-001"].explanation.lower()

    # Foreign product with importer
    fields_foreign["importer_name"] = "EuroGoods India Pvt Ltd, Mumbai"
    summary_valid_import = RuleEngine.evaluate_fields(fields_foreign)
    check_dict_v = {c.rule_code: c for c in summary_valid_import.checks}
    assert check_dict_v["LM-DECL-001"].status == "PASS"


def test_date_chronology_failure():
    """Test failure when expiry date precedes manufacturing date."""
    fields = get_sample_compliant_fields()
    fields["date_of_manufacture"] = "12/05/2024"
    fields["expiry_date"] = "10/01/2023"  # Precedes MFD

    summary = RuleEngine.evaluate_fields(fields)
    check_dict = {c.rule_code: c for c in summary.checks}
    assert check_dict["LM-DECL-002"].status == "FAIL"
    assert "precedes" in check_dict["LM-DECL-002"].explanation.lower()


def test_scoring_and_status_thresholds():
    """Test score penalty deductions and status categorization."""
    # Low severity failure (5 points deducted -> score 95.0 -> COMPLIANT)
    checks_low = [
        RuleCheckResult(rule_code="R1", rule_name="Test", status="PASS", severity="HIGH"),
        RuleCheckResult(rule_code="R2", rule_name="Test Low", status="WARN", severity="LOW"),
    ]
    score, status, _ = ComplianceScoreCalculator.calculate(checks_low)
    assert score == 97.5
    assert status == "COMPLIANT"

    # Critical & High failures (score < 70 -> NON_COMPLIANT)
    checks_bad = [
        RuleCheckResult(rule_code="R1", rule_name="MRP", status="FAIL", severity="CRITICAL"),
        RuleCheckResult(rule_code="R2", rule_name="Qty", status="FAIL", severity="CRITICAL"),
    ]
    score_bad, status_bad, stats = ComplianceScoreCalculator.calculate(checks_bad)
    assert score_bad == 50.0
    assert status_bad == "NON_COMPLIANT"
    assert stats["failed"] == 2
