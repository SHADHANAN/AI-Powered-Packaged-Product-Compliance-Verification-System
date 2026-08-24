import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck
from services.ocr_service.ocr import PaddleOCRService
from services.ocr_service.result import OCRResult, OCRLine
from services.explanation_service.llm import LLMExplanationService


def create_dummy_image_bytes(width: int = 200, height: int = 200) -> bytes:
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def mock_ocr(monkeypatch):
    sample_text = """BRITANNIA
Good Day Cashew Cookies
NET QTY 120 g
MRP Rs. 35.00
MFD 15/04/2024
USE BY 14/10/2024
BATCH NO. GD240415
MFD BY: Britannia Industries Ltd.
MADE IN INDIA
CUSTOMER CARE: 1800 425 4449, feedback@britindia.com
"""
    mock_ocr_result = OCRResult(
        success=True,
        text=sample_text,
        lines=[OCRLine(text=line, confidence=0.98) for line in sample_text.split("\n") if line.strip()],
        average_confidence=0.98,
        processing_time_ms=12.5,
    )
    monkeypatch.setattr(
        PaddleOCRService,
        "extract_text",
        lambda self, image_input, preprocess=True, strategy="standard": mock_ocr_result,
    )
    return mock_ocr_result


def test_phase10_complete_verification_pipeline(client: TestClient, mock_ocr):
    """Verifies complete end-to-end verification pipeline via POST /api/verify."""
    image_bytes = create_dummy_image_bytes()
    files = {"image": ("good_day.jpg", image_bytes, "image/jpeg")}
    data = {"preprocessing_strategy": "standard"}

    response = client.post("/api/verify", files=files, data=data)
    assert response.status_code == 200
    res = response.json()

    assert res["success"] is True
    assert res["verification_id"] is not None
    assert res["product_id"] is not None
    assert res["overall_status"] == "COMPLIANT"
    assert res["overall_score"] == 100.0
    assert len(res["extracted_fields"]) >= 5
    assert len(res["compliance_checks"]) >= 5
    assert res["explanation"] is not None
    assert "BRITANNIA" in res["ocr"]["text"]


def test_phase10_verification_history_and_details_api(client: TestClient, mock_ocr):
    """Verifies listing verification history and retrieving individual details."""
    # Perform verification to ensure a record exists
    image_bytes = create_dummy_image_bytes()
    files = {"image": ("good_day.jpg", image_bytes, "image/jpeg")}
    create_res = client.post("/api/verify", files=files)
    assert create_res.status_code == 200
    v_id = create_res.json()["verification_id"]

    # 1. Test History Listing
    list_res = client.get("/api/verifications?skip=0&limit=10")
    assert list_res.status_code == 200
    history = list_res.json()
    assert history["total"] >= 1
    assert any(item["id"] == v_id for item in history["items"])

    # 2. Test Verification Details
    detail_res = client.get(f"/api/verifications/{v_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == v_id
    assert detail["product"] is not None
    assert len(detail["extracted_fields"]) >= 1
    assert len(detail["compliance_checks"]) >= 1


def test_phase10_report_generation_api(client: TestClient, mock_ocr):
    """Verifies compliance audit report generation endpoint GET /api/verifications/{id}/report."""
    # Create verification record
    image_bytes = create_dummy_image_bytes()
    files = {"image": ("good_day.jpg", image_bytes, "image/jpeg")}
    create_res = client.post("/api/verify", files=files)
    v_id = create_res.json()["verification_id"]

    # Generate Report
    report_res = client.get(f"/api/verifications/{v_id}/report")
    assert report_res.status_code == 200
    report = report_res.json()

    assert report["verification_id"] == v_id
    assert report["overall_status"] == "COMPLIANT"
    assert report["overall_score"] == 100.0
    assert report["total_checks"] >= 5
    assert report["passed_checks"] >= 5
    assert len(report["recommendations"]) >= 1
    assert "# Legal Metrology Packaging Compliance Audit Report" in report["markdown_report"]


def test_phase10_report_not_found(client: TestClient):
    """Verifies report endpoint returns 404 for non-existent verification ID."""
    response = client.get("/api/verifications/999999/report")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["error"]["message"].lower()


def test_phase10_database_cascading_and_integrity(db_session: Session):
    """Verifies foreign key relationships, cascade deletions, and relational integrity."""
    prod = Product(
        product_name="Test Cascade Biscuits",
        brand_name="TestBrand",
        net_quantity="100",
        unit="g",
        mrp=30.0,
    )
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)

    ver = Verification(
        product_id=prod.id,
        verification_status="compliant",
        overall_score=100.0,
    )
    db_session.add(ver)
    db_session.commit()
    db_session.refresh(ver)

    field = ExtractedField(
        verification_id=ver.id,
        field_name="mrp",
        field_value="30.0",
        confidence=0.99,
    )
    check = ComplianceCheck(
        verification_id=ver.id,
        rule_code="LM-MANDATORY-003",
        rule_name="Maximum Retail Price (MRP)",
        status="PASS",
        severity="CRITICAL",
    )
    db_session.add_all([field, check])
    db_session.commit()

    ver_id = ver.id
    # Delete the parent product
    db_session.delete(prod)
    db_session.commit()

    # Assert cascaded deletion of verification, extracted fields, and compliance checks
    assert db_session.get(Verification, ver_id) is None
    assert db_session.query(ExtractedField).filter_by(verification_id=ver_id).first() is None
    assert db_session.query(ComplianceCheck).filter_by(verification_id=ver_id).first() is None


def test_phase10_deterministic_fallback_when_llm_fails(client: TestClient, monkeypatch):
    """Verifies full verification succeeds with deterministic explanation when LLM throws an exception."""
    sample_text = """PRODUCT XYZ
NET QTY 500 ml
MRP Rs. 99
MFD 01/2024
BATCH 999
MADE IN INDIA
"""
    mock_ocr_result = OCRResult(
        success=True,
        text=sample_text,
        lines=[OCRLine(text=line, confidence=0.95) for line in sample_text.split("\n") if line.strip()],
        average_confidence=0.95,
    )
    monkeypatch.setattr(
        PaddleOCRService,
        "extract_text",
        lambda self, image_input, preprocess=True, strategy="standard": mock_ocr_result,
    )

    # Force LLM generation to raise an unexpected runtime error
    def failing_llm(self, context):
        raise RuntimeError("External AI API Rate Limit Exceeded")

    monkeypatch.setattr(LLMExplanationService, "generate_explanation", failing_llm)

    image_bytes = create_dummy_image_bytes()
    files = {"image": ("fallback_test.jpg", image_bytes, "image/jpeg")}

    response = client.post("/api/verify", files=files)
    assert response.status_code == 200
    res = response.json()

    assert res["success"] is True
    assert res["explanation"] is not None
    assert res["explanation"]["ai_generated"] is False
    assert len(res["explanation"]["items"]) >= 1
