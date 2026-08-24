import re
from typing import Any, Dict, List, Optional
from services.compliance_service.models import RuleCheckResult

SUPPORTED_UNITS = {"g", "kg", "mg", "ml", "l", "pcs"}


def get_field_val(fields: Dict[str, Any], field_name: str) -> Optional[Any]:
    """Extracts value from either a dictionary of primitives or ExtractedField objects."""
    item = fields.get(field_name)
    if item is None:
        return None
    if isinstance(item, dict):
        return item.get("value")
    if hasattr(item, "field_value"):
        return item.field_value
    if hasattr(item, "value"):
        return item.value
    return item


def get_field_unit(fields: Dict[str, Any], field_name: str) -> Optional[str]:
    """Extracts unit from field dictionary or object."""
    item = fields.get(field_name)
    if item is None:
        return None
    if isinstance(item, dict):
        return item.get("unit")
    if hasattr(item, "unit"):
        return item.unit
    return None


def validate_mandatory_field(rule: Dict[str, Any], fields: Dict[str, Any]) -> RuleCheckResult:
    """
    Validates presence of a mandatory declaration.
    """
    field_name = rule["field"]
    val = get_field_val(fields, field_name)
    expected = rule.get("expected_value", f"{rule['rule_name']} must be declared")

    if val is not None and str(val).strip():
        return RuleCheckResult(
            rule_code=rule["rule_code"],
            rule_name=rule["rule_name"],
            status="PASS",
            severity=rule["severity"],
            expected_value=expected,
            actual_value=str(val),
            explanation=f"{rule['rule_name']} declaration is present ('{val}').",
        )
    else:
        return RuleCheckResult(
            rule_code=rule["rule_code"],
            rule_name=rule["rule_name"],
            status="FAIL",
            severity=rule["severity"],
            expected_value=expected,
            actual_value="Missing / Not Detected",
            explanation=f"{rule['rule_name']} declaration is missing from package labeling.",
        )


def validate_quantity_rules(rules: List[Dict[str, Any]], fields: Dict[str, Any]) -> List[RuleCheckResult]:
    """
    Validates Legal Metrology net quantity magnitude and standard metric unit rules.
    """
    results: List[RuleCheckResult] = []
    qty_val = get_field_val(fields, "net_quantity")
    qty_unit = get_field_unit(fields, "net_quantity") or get_field_val(fields, "unit")

    # QTY-001: Magnitude validation
    r1 = next((r for r in rules if r["rule_code"] == "LM-QTY-001"), None)
    if r1 and r1.get("enabled", True):
        if qty_val is None:
            results.append(
                RuleCheckResult(
                    rule_code=r1["rule_code"],
                    rule_name=r1["rule_name"],
                    status="FAIL",
                    severity=r1["severity"],
                    expected_value=r1["expected_value"],
                    actual_value="Missing",
                    explanation="Net quantity magnitude is missing.",
                )
            )
        else:
            try:
                numeric_qty = float(qty_val)
                if numeric_qty > 0:
                    results.append(
                        RuleCheckResult(
                            rule_code=r1["rule_code"],
                            rule_name=r1["rule_name"],
                            status="PASS",
                            severity=r1["severity"],
                            expected_value=r1["expected_value"],
                            actual_value=str(numeric_qty),
                            explanation=f"Net quantity {numeric_qty} is valid and greater than zero.",
                        )
                    )
                else:
                    results.append(
                        RuleCheckResult(
                            rule_code=r1["rule_code"],
                            rule_name=r1["rule_name"],
                            status="FAIL",
                            severity=r1["severity"],
                            expected_value=r1["expected_value"],
                            actual_value=str(numeric_qty),
                            explanation="Net quantity must be strictly greater than zero (found non-positive value).",
                        )
                    )
            except (ValueError, TypeError):
                results.append(
                    RuleCheckResult(
                        rule_code=r1["rule_code"],
                        rule_name=r1["rule_name"],
                        status="FAIL",
                        severity=r1["severity"],
                        expected_value=r1["expected_value"],
                        actual_value=str(qty_val),
                        explanation="Net quantity declaration is non-numeric.",
                    )
                )

    # QTY-002: Unit validation
    r2 = next((r for r in rules if r["rule_code"] == "LM-QTY-002"), None)
    if r2 and r2.get("enabled", True):
        if qty_unit is None or not str(qty_unit).strip():
            results.append(
                RuleCheckResult(
                    rule_code=r2["rule_code"],
                    rule_name=r2["rule_name"],
                    status="FAIL",
                    severity=r2["severity"],
                    expected_value=r2["expected_value"],
                    actual_value="Missing unit",
                    explanation="Net quantity is declared without a recognized measurement unit.",
                )
            )
        elif str(qty_unit).lower() in SUPPORTED_UNITS:
            results.append(
                RuleCheckResult(
                    rule_code=r2["rule_code"],
                    rule_name=r2["rule_name"],
                    status="PASS",
                    severity=r2["severity"],
                    expected_value=r2["expected_value"],
                    actual_value=str(qty_unit),
                    explanation=f"Measurement unit '{qty_unit}' is an approved Legal Metrology standard unit.",
                )
            )
        else:
            results.append(
                RuleCheckResult(
                    rule_code=r2["rule_code"],
                    rule_name=r2["rule_name"],
                    status="WARN",
                    severity=r2["severity"],
                    expected_value=r2["expected_value"],
                    actual_value=str(qty_unit),
                    explanation=f"Measurement unit '{qty_unit}' may not conform to standard metric units ({', '.join(sorted(SUPPORTED_UNITS))}).",
                )
            )

    return results


def validate_pricing_rules(rules: List[Dict[str, Any]], fields: Dict[str, Any]) -> List[RuleCheckResult]:
    """
    Validates Maximum Retail Price (MRP) values.
    """
    results: List[RuleCheckResult] = []
    mrp_val = get_field_val(fields, "mrp")

    r1 = next((r for r in rules if r["rule_code"] == "LM-PRICE-001"), None)
    if r1 and r1.get("enabled", True):
        if mrp_val is None:
            results.append(
                RuleCheckResult(
                    rule_code=r1["rule_code"],
                    rule_name=r1["rule_name"],
                    status="FAIL",
                    severity=r1["severity"],
                    expected_value=r1["expected_value"],
                    actual_value="Missing",
                    explanation="Maximum Retail Price (MRP) is missing.",
                )
            )
        else:
            try:
                numeric_mrp = float(mrp_val)
                if numeric_mrp > 0:
                    results.append(
                        RuleCheckResult(
                            rule_code=r1["rule_code"],
                            rule_name=r1["rule_name"],
                            status="PASS",
                            severity=r1["severity"],
                            expected_value=r1["expected_value"],
                            actual_value=f"Rs. {numeric_mrp:.2f}",
                            explanation=f"MRP Rs. {numeric_mrp:.2f} is present, positive, and compliant.",
                        )
                    )
                else:
                    results.append(
                        RuleCheckResult(
                            rule_code=r1["rule_code"],
                            rule_name=r1["rule_name"],
                            status="FAIL",
                            severity=r1["severity"],
                            expected_value=r1["expected_value"],
                            actual_value=str(numeric_mrp),
                            explanation="MRP must be strictly greater than zero.",
                        )
                    )
            except (ValueError, TypeError):
                results.append(
                    RuleCheckResult(
                        rule_code=r1["rule_code"],
                        rule_name=r1["rule_name"],
                        status="FAIL",
                        severity=r1["severity"],
                        expected_value=r1["expected_value"],
                        actual_value=str(mrp_val),
                        explanation="MRP value is non-numeric.",
                    )
                )

    return results


def validate_declaration_relationships(rules: List[Dict[str, Any]], fields: Dict[str, Any]) -> List[RuleCheckResult]:
    """
    Validates logical consistency between declarations (e.g. Domestic vs Imported rules, Date sequence).
    """
    results: List[RuleCheckResult] = []
    origin = get_field_val(fields, "country_of_origin")
    importer = get_field_val(fields, "importer_name")
    mfg = get_field_val(fields, "manufacturer_name")

    # DECL-001: Imported vs Domestic logic
    r1 = next((r for r in rules if r["rule_code"] == "LM-DECL-001"), None)
    if r1 and r1.get("enabled", True):
        is_foreign = origin and str(origin).strip().lower() not in {"india", "in", "ind"}
        if is_foreign or importer:
            # If foreign origin or importer declared, verify importer name is present
            if importer and str(importer).strip():
                results.append(
                    RuleCheckResult(
                        rule_code=r1["rule_code"],
                        rule_name=r1["rule_name"],
                        status="PASS",
                        severity=r1["severity"],
                        expected_value=r1["expected_value"],
                        actual_value=f"Importer: {importer}, Origin: {origin or 'Foreign'}",
                        explanation="Imported product declares valid importer and country of origin.",
                    )
                )
            else:
                results.append(
                    RuleCheckResult(
                        rule_code=r1["rule_code"],
                        rule_name=r1["rule_name"],
                        status="FAIL",
                        severity=r1["severity"],
                        expected_value=r1["expected_value"],
                        actual_value=f"Origin: {origin}, Importer: Missing",
                        explanation="Product is of foreign origin but lacks mandatory importer details.",
                    )
                )
        else:
            # Domestic product - not applicable for import requirement
            results.append(
                RuleCheckResult(
                    rule_code=r1["rule_code"],
                    rule_name=r1["rule_name"],
                    status="NOT_APPLICABLE",
                    severity=r1["severity"],
                    expected_value=r1["expected_value"],
                    actual_value="Domestic Product",
                    explanation="Product is of domestic origin; separate importer declaration is not applicable.",
                )
            )

    # DECL-002: Manufacturing and Expiry Date Consistency
    r2 = next((r for r in rules if r["rule_code"] == "LM-DECL-002"), None)
    if r2 and r2.get("enabled", True):
        mfd = get_field_val(fields, "date_of_manufacture")
        exp = get_field_val(fields, "expiry_date")

        if mfd and exp:
            # Attempt basic year/month comparison if dates match DD/MM/YYYY or MM/YYYY
            date_regex = re.compile(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})")
            mfd_match = date_regex.search(str(mfd))
            exp_match = date_regex.search(str(exp))

            if mfd_match and exp_match:
                try:
                    mfd_year = int(mfd_match.group(3))
                    if mfd_year < 100:
                        mfd_year += 2000
                    mfd_month = int(mfd_match.group(2))

                    exp_year = int(exp_match.group(3))
                    if exp_year < 100:
                        exp_year += 2000
                    exp_month = int(exp_match.group(2))

                    if (exp_year, exp_month) < (mfd_year, mfd_month):
                        results.append(
                            RuleCheckResult(
                                rule_code=r2["rule_code"],
                                rule_name=r2["rule_name"],
                                status="FAIL",
                                severity=r2["severity"],
                                expected_value=r2["expected_value"],
                                actual_value=f"MFD: {mfd}, EXP: {exp}",
                                explanation="Expiry date precedes the date of manufacture.",
                            )
                        )
                    else:
                        results.append(
                            RuleCheckResult(
                                rule_code=r2["rule_code"],
                                rule_name=r2["rule_name"],
                                status="PASS",
                                severity=r2["severity"],
                                expected_value=r2["expected_value"],
                                actual_value=f"MFD: {mfd}, EXP: {exp}",
                                explanation="Date of manufacture and expiry dates are chronologically consistent.",
                            )
                        )
                except Exception:
                    results.append(
                        RuleCheckResult(
                            rule_code=r2["rule_code"],
                            rule_name=r2["rule_name"],
                            status="PASS",
                            severity=r2["severity"],
                            expected_value=r2["expected_value"],
                            actual_value=f"MFD: {mfd}, EXP: {exp}",
                            explanation="Both manufacture and expiry dates are declared.",
                        )
                    )
            else:
                results.append(
                    RuleCheckResult(
                        rule_code=r2["rule_code"],
                        rule_name=r2["rule_name"],
                        status="PASS",
                        severity=r2["severity"],
                        expected_value=r2["expected_value"],
                        actual_value=f"MFD: {mfd}, EXP: {exp}",
                        explanation="Both manufacture and expiry/best-before dates are present.",
                    )
                )
        else:
            results.append(
                RuleCheckResult(
                    rule_code=r2["rule_code"],
                    rule_name=r2["rule_name"],
                    status="NOT_APPLICABLE",
                    severity=r2["severity"],
                    expected_value=r2["expected_value"],
                    actual_value="Incomplete date pair",
                    explanation="Date sequence check requires both manufacture and expiry declarations.",
                )
            )

    return results
