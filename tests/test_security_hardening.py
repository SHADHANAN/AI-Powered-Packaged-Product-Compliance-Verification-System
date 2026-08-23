import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.config import Settings
from backend.utils.logger import mask_sensitive_data
from services.ocr_service.ocr import PaddleOCRService
from services.ocr_service.result import OCRResult, OCRLine
from services.ocr_service.image_utils import (
    sanitize_filename,
    is_valid_mime_type,
    is_valid_extension,
    validate_image_bytes,
    MAX_IMAGE_SIZE_BYTES,
)


def test_security_filename_sanitization():
    """Verifies that malicious directory traversal filenames are stripped safely."""
    assert sanitize_filename("../../../etc/passwd.jpg") == "passwd.jpg"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.png") == "calc.png"
    assert sanitize_filename("safe_label.jpg") == "safe_label.jpg"
    assert sanitize_filename("foo\x00bar.png") == "foobar.png"
    assert sanitize_filename("") == "uploaded_image.jpg"
    assert sanitize_filename(None) == "uploaded_image.jpg"


def test_security_mime_and_extension_validation():
    """Verifies MIME type and extension checking."""
    assert is_valid_extension("packet.jpg") is True
    assert is_valid_extension("packet.PNG") is True
    assert is_valid_extension("packet.webp") is True
    assert is_valid_extension("script.py") is False
    assert is_valid_extension("malware.exe") is False

    assert is_valid_mime_type("image/jpeg") is True
    assert is_valid_mime_type("image/png; charset=utf-8") is True
    assert is_valid_mime_type("application/pdf") is False
    assert is_valid_mime_type("text/html") is False


def test_security_oversized_image_rejection():
    """Verifies that oversized image payloads are rejected."""
    oversized_bytes = b"X" * (MAX_IMAGE_SIZE_BYTES + 1024)
    is_valid, err, dims = validate_image_bytes(oversized_bytes, filename="large.jpg")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err


def test_security_invalid_mime_type_upload(client: TestClient):
    """Verifies that uploading a non-image MIME type is rejected with 400 Bad Request."""
    files = {"image": ("dummy.txt", b"plain text data", "text/plain")}
    response = client.post("/api/verify", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file" in data["error"]["message"] or "Invalid" in data["error"]["message"]


def test_security_path_traversal_upload(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """Verifies that uploads with path-traversal filenames are safely handled."""
    mock_ocr_result = OCRResult(
        success=True,
        text="BRAND NAME\nProduct A\nNET QTY 100 g\nMRP Rs. 50\nMFD 01/2024\nBATCH 1234",
        lines=[
            OCRLine(text="BRAND NAME", confidence=0.98),
            OCRLine(text="Product A", confidence=0.95),
            OCRLine(text="NET QTY 100 g", confidence=0.97),
            OCRLine(text="MRP Rs. 50", confidence=0.99),
            OCRLine(text="MFD 01/2024", confidence=0.94),
            OCRLine(text="BATCH 1234", confidence=0.96),
        ],
        average_confidence=0.965,
        processing_time_ms=10.0,
    )
    monkeypatch.setattr(
        PaddleOCRService,
        "extract_text",
        lambda self, image_input, preprocess=True, strategy="standard": mock_ocr_result,
    )

    # Create valid synthetic image
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    files = {"image": ("../../../../etc/shadow.jpg", image_bytes, "image/jpeg")}
    response = client.post("/api/verify", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_security_cors_settings_parsing():
    """Verifies that CORS origins are parsed correctly from string or list formats."""
    # Comma-separated
    s1 = Settings(CORS_ORIGINS="http://localhost:3000, http://127.0.0.1:3000")
    assert "http://localhost:3000" in s1.CORS_ORIGINS
    assert "http://127.0.0.1:3000" in s1.CORS_ORIGINS

    # JSON Array string
    s2 = Settings(CORS_ORIGINS='["http://example.com", "http://app.local"]')
    assert "http://example.com" in s2.CORS_ORIGINS
    assert "http://app.local" in s2.CORS_ORIGINS


def test_security_logger_masking():
    """Verifies that sensitive tokens and API keys are masked in log strings."""
    secret_log = 'User logged with api_key="AIzaSyA123456789SecretKeyXYZ" and token: "bearer-token-12345678"'
    masked = mask_sensitive_data(secret_log)
    assert "AIzaSyA123456789SecretKeyXYZ" not in masked
    assert "bearer-token-12345678" not in masked


def test_security_unhandled_exception_no_stack_leakage(client: TestClient):
    """Verifies that 404/500 errors return structured JSON without stack trace leakage."""
    response = client.get("/api/non_existent_endpoint_12345")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Traceback" not in str(data)
