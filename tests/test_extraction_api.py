from fastapi.testclient import TestClient


def test_extraction_api_success(client: TestClient):
    """Test POST /api/extract with comprehensive OCR text."""
    payload = {
        "text": """LAY'S
Chile Limón
Flavour
PROPRIETARY FOOD - POTATO CHIPS
NET QTY 50 g
MRP Rs. 20.00
MFD 12/05/2024
USE BY 11/11/2024
BATCH NO. 24E1205
MFD. & MKTG. BY: PepsiCo India Holdings Pvt. Ltd.
MADE IN INDIA
CUSTOMER CARE: 1800 22 4020, consumer.feedback@pepsico.com
FSSAI LIC NO: 10014064000435
"""
    }
    response = client.post("/api/extract", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["field_count"] >= 8
    assert data["average_confidence"] > 0.8
    assert data["raw_text"] is not None

    # Check field names
    extracted_names = [f["field_name"] for f in data["fields"]]
    assert "mrp" in extracted_names
    assert "net_quantity" in extracted_names
    assert "date_of_manufacture" in extracted_names
    assert "batch_number" in extracted_names
    assert "country_of_origin" in extracted_names

    # Check MRP field structure
    mrp_field = next(f for f in data["fields"] if f["field_name"] == "mrp")
    assert mrp_field["value"] == 20.0
    assert mrp_field["confidence"] >= 0.8
    assert mrp_field["source_text"] is not None


def test_extraction_api_single_field(client: TestClient):
    """Test POST /api/extract with single declaration."""
    payload = {"text": "MRP Rs. 500.00 (Inclusive of all taxes)"}
    response = client.post("/api/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["field_count"] >= 1
    assert data["fields"][0]["field_name"] == "mrp"
    assert data["fields"][0]["value"] == 500.0


def test_extraction_api_empty_text_error(client: TestClient):
    """Test POST /api/extract with empty text returns 422 or 400."""
    response = client.post("/api/extract", json={"text": ""})
    assert response.status_code in [400, 422]


def test_extraction_api_missing_payload(client: TestClient):
    """Test POST /api/extract with missing payload returns 422."""
    response = client.post("/api/extract", json={})
    assert response.status_code == 422
