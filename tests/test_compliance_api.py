from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck


def test_compliance_api_standalone_fields(client: TestClient):
    """Test POST /api/compliance/evaluate with direct extracted_fields list."""
    payload = {
        "extracted_fields": [
            {"field_name": "product_name", "value": "Whole Wheat Bread"},
            {"field_name": "net_quantity", "value": 400, "unit": "g"},
            {"field_name": "unit", "value": "g"},
            {"field_name": "mrp", "value": 45.0},
            {"field_name": "manufacturer_name", "value": "Harvest Breads Ltd, Bangalore"},
            {"field_name": "date_of_manufacture", "value": "10/05/2024"},
            {"field_name": "batch_number", "value": "BR-1005"},
            {"field_name": "country_of_origin", "value": "India"},
            {"field_name": "customer_care_details", "value": "1800 111 222"},
        ]
    }
    response = client.post("/api/compliance/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] == "COMPLIANT"
    assert data["overall_score"] == 100.0
    assert data["verification_id"] is None
    assert len(data["checks"]) >= 8
    assert data["passed_count"] >= 8
    assert data["failed_count"] == 0


def test_compliance_api_with_db_verification(client: TestClient, db_session: Session):
    """Test POST /api/compliance/evaluate persists ComplianceCheck records and updates Verification."""
    # Seed Product and Verification in DB
    product = Product(
        product_name="Almond Butter",
        brand_name="NuttyDelight",
        country_of_origin="India",
        net_quantity="200",
        unit="g",
        mrp=320.0,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    verification = Verification(
        product_id=product.id,
        verification_status="pending",
    )
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)

    # Seed ExtractedField records for this verification
    fields = [
        ExtractedField(verification_id=verification.id, field_name="product_name", field_value="Almond Butter", confidence=0.98),
        ExtractedField(verification_id=verification.id, field_name="net_quantity", field_value="200", confidence=0.95),
        ExtractedField(verification_id=verification.id, field_name="unit", field_value="g", confidence=0.95),
        ExtractedField(verification_id=verification.id, field_name="mrp", field_value="320.0", confidence=0.99),
        ExtractedField(verification_id=verification.id, field_name="manufacturer_name", field_value="Nutty Foods Ltd, Pune", confidence=0.92),
        ExtractedField(verification_id=verification.id, field_name="country_of_origin", field_value="India", confidence=0.97),
        ExtractedField(verification_id=verification.id, field_name="date_of_manufacture", field_value="01/2025", confidence=0.94),
        ExtractedField(verification_id=verification.id, field_name="batch_number", field_value="NB-2025-01", confidence=0.96),
        ExtractedField(verification_id=verification.id, field_name="customer_care_details", field_value="care@nutty.com", confidence=0.91),
    ]
    db_session.add_all(fields)
    db_session.commit()

    # Call compliance evaluation API
    response = client.post("/api/compliance/evaluate", json={"verification_id": verification.id})
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["verification_id"] == verification.id
    assert data["status"] == "COMPLIANT"
    assert data["overall_score"] == 100.0

    # Verify DB persistence
    db_session.refresh(verification)
    assert verification.verification_status == "compliant"
    assert verification.overall_score == 100.0
    assert verification.completed_at is not None

    checks_in_db = db_session.query(ComplianceCheck).filter(ComplianceCheck.verification_id == verification.id).all()
    assert len(checks_in_db) >= 8
    rule_codes = [c.rule_code for c in checks_in_db]
    assert "LM-MANDATORY-001" in rule_codes
    assert "LM-MANDATORY-002" in rule_codes


def test_compliance_api_verification_not_found(client: TestClient):
    """Test 404 response for non-existent verification_id."""
    response = client.post("/api/compliance/evaluate", json={"verification_id": 99999})
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 404
    assert "not found" in body["error"]["message"].lower()


def test_compliance_api_empty_payload(client: TestClient):
    """Test 422 response when neither verification_id nor extracted_fields is supplied."""
    response = client.post("/api/compliance/evaluate", json={})
    assert response.status_code == 422
