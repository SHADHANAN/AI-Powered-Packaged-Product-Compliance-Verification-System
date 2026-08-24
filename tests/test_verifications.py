from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck


def test_get_verification_by_id(client: TestClient, db_session: Session):
    """Test retrieving verification details with product, extracted fields, and compliance checks."""
    # Seed a complete verification session
    product = Product(
        product_name="Pure Ghee",
        brand_name="DesiFarm",
        manufacturer_name="DesiFarm Dairy Ltd",
        country_of_origin="India",
        net_quantity="500",
        unit="ml",
        mrp=350.0,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    verification = Verification(
        product_id=product.id,
        verification_status="compliant",
        overall_score=98.0,
        source_image_path="/storage/labels/ghee_label_01.jpg",
    )
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)

    field1 = ExtractedField(
        verification_id=verification.id,
        field_name="mrp",
        field_value="Rs. 350.00",
        confidence=0.99,
        source_text="MRP: Rs. 350.00 (Incl. of all taxes)",
    )
    field2 = ExtractedField(
        verification_id=verification.id,
        field_name="net_quantity",
        field_value="500 ml",
        confidence=0.97,
        source_text="Net Qty: 500 ml",
    )
    check1 = ComplianceCheck(
        verification_id=verification.id,
        rule_code="LM-01",
        rule_name="MRP Declaration Rule",
        status="pass",
        expected_value="MRP inclusive of taxes",
        actual_value="Rs. 350.00",
        explanation="MRP is clearly indicated with tax declaration.",
        severity="critical",
    )
    check2 = ComplianceCheck(
        verification_id=verification.id,
        rule_code="LM-02",
        rule_name="Net Quantity Standard Unit Rule",
        status="pass",
        expected_value="Standard metric unit (ml/L/g/kg)",
        actual_value="500 ml",
        explanation="Net quantity uses correct Legal Metrology unit.",
        severity="high",
    )
    db_session.add_all([field1, field2, check1, check2])
    db_session.commit()

    # Query API endpoint
    response = client.get(f"/api/verifications/{verification.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == verification.id
    assert data["product_id"] == product.id
    assert data["verification_status"] == "compliant"
    assert data["overall_score"] == 98.0
    assert data["source_image_path"] == "/storage/labels/ghee_label_01.jpg"

    # Verify nested product
    assert data["product"] is not None
    assert data["product"]["product_name"] == "Pure Ghee"
    assert data["product"]["brand_name"] == "DesiFarm"

    # Verify nested extracted fields
    assert len(data["extracted_fields"]) == 2
    field_names = [f["field_name"] for f in data["extracted_fields"]]
    assert "mrp" in field_names
    assert "net_quantity" in field_names

    # Verify nested compliance checks
    assert len(data["compliance_checks"]) == 2
    rule_codes = [c["rule_code"] for c in data["compliance_checks"]]
    assert "LM-01" in rule_codes
    assert "LM-02" in rule_codes


def test_get_verification_not_found(client: TestClient):
    """Test 404 response for non-existent verification ID."""
    response = client.get("/api/verifications/88888")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 404
    assert "not found" in body["error"]["message"].lower()
