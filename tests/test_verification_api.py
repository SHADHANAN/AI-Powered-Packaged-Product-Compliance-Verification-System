import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from services.ocr_service.ocr import PaddleOCRService
from services.ocr_service.result import OCRResult, OCRLine


def create_dummy_image_bytes(width: int = 200, height: int = 200, format: str = "JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_verify_api_success(client: TestClient, monkeypatch):
    """Test POST /api/verify with complete pipeline orchestration."""
    sample_text = """LAY'S
Chile Limón
NET QTY 50 g
MRP Rs. 20.00
MFD 12/05/2024
USE BY 11/11/2024
BATCH NO. 24E1205
MFD. & MKTG. BY: PepsiCo India Holdings Pvt. Ltd.
MADE IN INDIA
CUSTOMER CARE: 1800 22 4020, consumer.feedback@pepsico.com
"""
    mock_ocr_result = OCRResult(
        success=True,
        text=sample_text,
        lines=[OCRLine(text=line, confidence=0.98) for line in sample_text.split("\n") if line.strip()],
        average_confidence=0.98,
    )

    monkeypatch.setattr(
        PaddleOCRService,
        "extract_text",
        lambda self, image_input, preprocess=True, strategy="standard": mock_ocr_result,
    )

    image_bytes = create_dummy_image_bytes()
    files = {"image": ("lays_chips.jpg", image_bytes, "image/jpeg")}
    data = {"preprocessing_strategy": "standard"}

    response = client.post("/api/verify", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["success"] is True
    assert res_data["verification_id"] is not None
    assert res_data["product_id"] is not None
    assert res_data["overall_status"] == "COMPLIANT"
    assert res_data["overall_score"] == 100.0

    # OCR block
    assert res_data["ocr"] is not None
    assert "LAY'S" in res_data["ocr"]["text"]

    # Extracted fields block
    assert len(res_data["extracted_fields"]) >= 8

    # Compliance checks block
    assert len(res_data["compliance_checks"]) >= 8

    # Explanation block
    assert res_data["explanation"] is not None
    assert len(res_data["explanation"]["items"]) >= 8
    assert len(res_data["explanation"]["recommendations"]) >= 1


def test_verify_api_corrupted_image(client: TestClient):
    """Test POST /api/verify with corrupted image payload returns 400."""
    files = {"image": ("corrupted.png", b"NOT_IMAGE_DATA", "image/png")}
    response = client.post("/api/verify", files=files)
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 400


def test_verify_api_unsupported_extension(client: TestClient):
    """Test POST /api/verify with unsupported file extension returns 400."""
    files = {"image": ("label_doc.txt", b"plain text data", "text/plain")}
    response = client.post("/api/verify", files=files)
    assert response.status_code == 400


def test_verify_api_missing_file(client: TestClient):
    """Test POST /api/verify without image file returns 422."""
    response = client.post("/api/verify", data={"preprocessing_strategy": "standard"})
    assert response.status_code == 422
