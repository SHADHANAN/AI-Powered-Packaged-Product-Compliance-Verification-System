from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.models import Product, Verification, ComplianceCheck


def test_explanation_api_standalone_checks(client: TestClient):
    """Test POST /api/explanation with direct checks payload."""
    payload = {
        "checks": [
            {
                "rule_code": "LM-MANDATORY-001",
                "rule_name": "Product Name",
                "status": "PASS",
                "severity": "HIGH",
                "expected_value": "Declared",
                "actual_value": "Potato Chips",
                "explanation": "Product name is present.",
            },
            {
                "rule_code": "LM-MANDATORY-003",
                "rule_name": "Maximum Retail Price",
                "status": "FAIL",
                "severity": "CRITICAL",
                "expected_value": "Declared in INR",
                "actual_value": "Missing",
                "explanation": "MRP is missing.",
            },
        ],
        "overall_score": 75.0,
        "status": "PARTIALLY_COMPLIANT",
    }
    response = client.post("/api/explanation", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["overall_status"] == "PARTIALLY_COMPLIANT"
    assert data["overall_score"] == 75.0
    assert len(data["explanations"]) == 2
    assert len(data["recommendations"]) >= 1
    assert data["verification_id"] is None


def test_explanation_api_with_db_verification(client: TestClient, db_session: Session):
    """Test POST /api/explanation loading checks from database verification record."""
    product = Product(
        product_name="Orange Juice",
        brand_name="FreshFruit",
        country_of_origin="India",
        net_quantity="1",
        unit="l",
        mrp=95.0,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    verification = Verification(
        product_id=product.id,
        verification_status="compliant",
        overall_score=100.0,
    )
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)

    check = ComplianceCheck(
        verification_id=verification.id,
        rule_code="LM-MANDATORY-001",
        rule_name="Product Name",
        status="pass",
        severity="high",
        expected_value="Declared",
        actual_value="Orange Juice",
        explanation="Product name is present.",
    )
    db_session.add(check)
    db_session.commit()

    response = client.post("/api/explanation", json={"verification_id": verification.id})
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["verification_id"] == verification.id
    assert data["overall_status"] == "COMPLIANT"
    assert data["overall_score"] == 100.0
    assert len(data["explanations"]) >= 1


def test_explanation_api_verification_not_found(client: TestClient):
    """Test 404 response for invalid verification_id."""
    response = client.post("/api/explanation", json={"verification_id": 88888})
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 404


def test_explanation_api_empty_payload(client: TestClient):
    """Test 422 response for empty payload."""
    response = client.post("/api/explanation", json={})
    assert response.status_code == 422
