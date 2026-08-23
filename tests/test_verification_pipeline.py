import io
import pytest
from PIL import Image
from sqlalchemy.orm import Session
from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck
from services.verification_service.pipeline import VerificationPipeline
from services.ocr_service.ocr import PaddleOCRService
from services.ocr_service.result import OCRResult, OCRLine
from services.explanation_service.llm import LLMExplanationService


def create_dummy_image_bytes(width: int = 300, height: int = 300, format: str = "JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_complete_pipeline_success(db_session: Session, monkeypatch):
    """Test full verification pipeline with mocked OCR recognizing a compliant product."""
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
    result = VerificationPipeline.run(
        db=db_session,
        image_bytes=image_bytes,
        filename="test_lays.jpg",
    )

    assert result.success is True
    assert result.verification_id is not None
    assert result.product_id is not None
    assert result.overall_status == "COMPLIANT"
    assert result.overall_score == 100.0
    assert result.stages.image_validation is True
    assert result.stages.ocr is True
    assert result.stages.extraction is True
    assert result.stages.database_persist is True
    assert result.stages.compliance_evaluation is True
    assert result.stages.explanation_generation is True

    # Verify Database Persistence
    verification = db_session.query(Verification).filter(Verification.id == result.verification_id).first()
    assert verification is not None
    assert verification.product_id == result.product_id
    assert verification.verification_status == "compliant"
    assert verification.overall_score == 100.0

    product = db_session.query(Product).filter(Product.id == result.product_id).first()
    assert product is not None
    assert product.brand_name == "LAY'S"

    fields = db_session.query(ExtractedField).filter(ExtractedField.verification_id == verification.id).all()
    assert len(fields) >= 8

    checks = db_session.query(ComplianceCheck).filter(ComplianceCheck.verification_id == verification.id).all()
    assert len(checks) >= 8


def test_pipeline_corrupted_image(db_session: Session):
    """Test pipeline response on corrupted image bytes."""
    corrupted_bytes = b"NOT_A_VALID_IMAGE_DATA_HEADER"
    result = VerificationPipeline.run(
        db=db_session,
        image_bytes=corrupted_bytes,
        filename="corrupt.jpg",
    )
    assert result.success is False
    assert result.stages.image_validation is False
    assert "image validation failed" in result.error_message.lower()


def test_pipeline_deterministic_fallback_when_llm_fails(db_session: Session, monkeypatch):
    """Test pipeline gracefully produces deterministic explanations when LLM is unavailable."""
    sample_text = "NET QTY 50 g\nMRP Rs. 20.00\nMADE IN INDIA\n"
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

    image_bytes = create_dummy_image_bytes()
    # Provide an LLM service with empty API key
    llm_service = LLMExplanationService(provider="gemini", api_key="")
    result = VerificationPipeline.run(
        db=db_session,
        image_bytes=image_bytes,
        filename="fallback_test.jpg",
        llm_service=llm_service,
    )

    assert result.success is True
    assert result.explanation["ai_generated"] is False  # Fallback was engaged
    assert len(result.explanation["items"]) >= 1
