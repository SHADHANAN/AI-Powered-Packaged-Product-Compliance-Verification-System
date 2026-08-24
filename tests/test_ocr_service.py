import io
import pytest
import numpy as np
from PIL import Image, ImageDraw

from services.ocr_service.image_utils import (
    validate_image_bytes,
    load_image,
    ImageValidationError,
    temp_image_file,
)
from services.ocr_service.preprocess import (
    preprocess_image,
    resize_image,
    to_grayscale,
    enhance_contrast,
    reduce_noise,
    binarize,
)
from services.ocr_service.result import OCRLine, OCRResult
from services.ocr_service.ocr import PaddleOCRService


def create_test_image(text: str = "Test Product Label", size=(400, 200), fmt="PNG") -> bytes:
    """Helper to generate a real, valid image in memory."""
    img = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill=(0, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return buffer.getvalue()


class MockPaddleOCREngine:
    """Mock PaddleOCR engine to avoid heavy downloads/network calls during tests."""

    def __init__(self, return_empty: bool = False, custom_lines=None):
        self.return_empty = return_empty
        self.custom_lines = custom_lines

    def ocr(self, img, cls=True):
        if self.return_empty:
            return [[]]
        if self.custom_lines is not None:
            return [self.custom_lines]
        return [
            [
                [
                    [[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]],
                    ("BRAND NAME: PureOrganics", 0.985),
                ],
                [
                    [[10.0, 60.0], [120.0, 60.0], [120.0, 90.0], [10.0, 90.0]],
                    ("NET QTY: 500 g", 0.942),
                ],
                [
                    [[10.0, 100.0], [110.0, 100.0], [110.0, 130.0], [10.0, 130.0]],
                    ("MRP: Rs. 250.00", 0.963),
                ],
            ]
        ]


def test_image_validation_valid():
    """Test image validation on valid JPEG and PNG bytes."""
    png_bytes = create_test_image(fmt="PNG")
    is_valid, err, dims = validate_image_bytes(png_bytes, "label.png")
    assert is_valid is True
    assert err is None
    assert dims == (400, 200)

    jpg_bytes = create_test_image(fmt="JPEG")
    is_valid_jpg, err_jpg, dims_jpg = validate_image_bytes(jpg_bytes, "label.jpg")
    assert is_valid_jpg is True
    assert err_jpg is None


def test_image_validation_corrupted_and_empty():
    """Test rejection of empty and corrupted image files."""
    # Empty bytes
    is_valid, err, _ = validate_image_bytes(b"", "empty.jpg")
    assert is_valid is False
    assert "empty" in err.lower()

    # Corrupted bytes
    corrupted_bytes = b"NOT_A_VALID_IMAGE_HEADER_RANDOM_GARBAGE_12345"
    is_valid_c, err_c, _ = validate_image_bytes(corrupted_bytes, "bad.jpg")
    assert is_valid_c is False
    assert "corrupted" in err_c.lower() or "cannot identify" in err_c.lower()


def test_image_validation_unsupported_extension():
    """Test rejection of unsupported file extensions."""
    png_bytes = create_test_image()
    is_valid, err, _ = validate_image_bytes(png_bytes, "label.pdf")
    assert is_valid is False
    assert "unsupported" in err.lower()


def test_image_validation_too_small():
    """Test rejection of micro dimensions."""
    micro_img = create_test_image(size=(8, 8))
    is_valid, err, _ = validate_image_bytes(micro_img, "tiny.png")
    assert is_valid is False
    assert "too small" in err.lower()


def test_image_loading_and_temp_file():
    """Test loading image into NumPy array and temp file context manager."""
    img_bytes = create_test_image(size=(100, 80))
    arr = load_image(img_bytes)
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (80, 100, 3)

    # Test temp image context manager
    with temp_image_file(img_bytes, suffix=".png") as temp_p:
        assert temp_p.exists()
    assert not temp_p.exists()


def test_preprocessing_pipeline():
    """Test all preprocessing functions: resize, grayscale, contrast, noise reduction, binarization."""
    img_bytes = create_test_image(size=(3000, 1000))
    raw_arr = load_image(img_bytes)

    # 1. Resize
    resized, scale = resize_image(raw_arr, max_dimension=2000)
    assert scale < 1.0
    assert max(resized.shape[:2]) == 2000

    # 2. Grayscale
    gray = to_grayscale(raw_arr)
    assert len(gray.shape) == 2

    # 3. Contrast enhancement
    clahe_img = enhance_contrast(gray)
    assert clahe_img.shape == gray.shape

    # 4. Noise reduction
    denoised = reduce_noise(raw_arr)
    assert denoised.shape == raw_arr.shape

    # 5. Binarize
    binary = binarize(gray, method="otsu")
    assert set(np.unique(binary)).issubset({0, 255})

    # 6. Full strategy tests
    processed_std, meta_std = preprocess_image(raw_arr, strategy="standard")
    assert meta_std["strategy"] == "standard"

    processed_clahe, meta_clahe = preprocess_image(raw_arr, strategy="grayscale_clahe")
    assert len(processed_clahe.shape) == 2

    processed_bin, meta_bin = preprocess_image(raw_arr, strategy="binarized")
    assert len(processed_bin.shape) == 2


def test_paddle_ocr_service_mocked():
    """Test PaddleOCRService structured extraction with mocked engine."""
    mock_engine = MockPaddleOCREngine()
    service = PaddleOCRService(ocr_engine=mock_engine)

    valid_bytes = create_test_image()
    result: OCRResult = service.extract_text(valid_bytes, preprocess=True)

    assert result.success is True
    assert len(result.lines) == 3
    assert "BRAND NAME: PureOrganics" in result.text
    assert "NET QTY: 500 g" in result.text
    assert "MRP: Rs. 250.00" in result.text
    assert result.average_confidence > 0.95
    assert result.processing_time_ms is not None

    # Check line structure
    line0 = result.lines[0]
    assert line0.text == "BRAND NAME: PureOrganics"
    assert line0.confidence == 0.985
    assert line0.bounding_box == [[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]]


def test_paddle_ocr_service_empty_image():
    """Test PaddleOCRService handling image with no detected text."""
    empty_engine = MockPaddleOCREngine(return_empty=True)
    service = PaddleOCRService(ocr_engine=empty_engine)

    blank_bytes = create_test_image(text="")
    result: OCRResult = service.extract_text(blank_bytes)

    assert result.success is True
    assert result.text == ""
    assert len(result.lines) == 0
    assert result.average_confidence == 0.0


def test_paddle_ocr_service_corrupted_input():
    """Test PaddleOCRService gracefully returns failure on corrupted input."""
    service = PaddleOCRService(ocr_engine=MockPaddleOCREngine())
    result: OCRResult = service.extract_text(b"corrupted_bytes_123")

    assert result.success is False
    assert result.text == ""
    assert result.error_message is not None
    assert "corrupted" in result.error_message.lower() or "invalid" in result.error_message.lower()
