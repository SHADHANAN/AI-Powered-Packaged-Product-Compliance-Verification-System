import io
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from services.ocr_service.ocr import set_ocr_service, PaddleOCRService
from tests.test_ocr_service import MockPaddleOCREngine


def create_test_image_file(text: str = "Net Qty: 250 g", fmt: str = "JPEG") -> io.BytesIO:
    """Helper creating an in-memory image file."""
    img = Image.new("RGB", (300, 150), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill=(0, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    buffer.seek(0)
    return buffer


def test_ocr_api_valid_image(client: TestClient):
    """Test POST /api/ocr with valid image upload."""
    # Inject mock OCR engine
    mock_service = PaddleOCRService(ocr_engine=MockPaddleOCREngine())
    set_ocr_service(mock_service)

    img_buf = create_test_image_file(text="BRAND: PureHarvest")
    files = {"file": ("label.jpg", img_buf, "image/jpeg")}

    response = client.post("/api/ocr", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "BRAND NAME: PureOrganics" in data["text"]
    assert len(data["lines"]) == 3
    assert data["average_confidence"] > 0.9
    assert data["processing_time_ms"] is not None

    # Check line fields
    first_line = data["lines"][0]
    assert "text" in first_line
    assert "confidence" in first_line
    assert "bounding_box" in first_line


def test_ocr_api_with_strategy_param(client: TestClient):
    """Test POST /api/ocr with preprocessing strategy query parameter."""
    mock_service = PaddleOCRService(ocr_engine=MockPaddleOCREngine())
    set_ocr_service(mock_service)

    img_buf = create_test_image_file(text="Commodity: Wheat Flour", fmt="PNG")
    files = {"file": ("package.png", img_buf, "image/png")}

    response = client.post("/api/ocr?strategy=grayscale_clahe", files=files)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_ocr_api_corrupted_image(client: TestClient):
    """Test POST /api/ocr with corrupted image file returns 400 Bad Request."""
    corrupted_buf = io.BytesIO(b"GARBAGE_NOT_AN_IMAGE_FILE_DATA_123456789")
    files = {"file": ("corrupted.jpg", corrupted_buf, "image/jpeg")}

    response = client.post("/api/ocr", files=files)
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 400
    assert "corrupted" in body["error"]["message"].lower() or "invalid" in body["error"]["message"].lower()


def test_ocr_api_unsupported_extension(client: TestClient):
    """Test POST /api/ocr with unsupported extension returns 400 Bad Request."""
    fake_pdf = io.BytesIO(b"%PDF-1.4 header text")
    files = {"file": ("document.pdf", fake_pdf, "application/pdf")}

    response = client.post("/api/ocr", files=files)
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert "unsupported" in body["error"]["message"].lower()


def test_ocr_api_missing_file(client: TestClient):
    """Test POST /api/ocr with missing file returns 422 Unprocessable Entity."""
    response = client.post("/api/ocr", data={})
    assert response.status_code == 422
    assert "error" in response.json()


def test_ocr_api_empty_detection(client: TestClient):
    """Test POST /api/ocr when OCR engine detects no text."""
    empty_service = PaddleOCRService(ocr_engine=MockPaddleOCREngine(return_empty=True))
    set_ocr_service(empty_service)

    blank_buf = create_test_image_file(text="", fmt="PNG")
    files = {"file": ("blank.png", blank_buf, "image/png")}

    response = client.post("/api/ocr", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == ""
    assert len(data["lines"]) == 0
    assert data["average_confidence"] == 0.0
