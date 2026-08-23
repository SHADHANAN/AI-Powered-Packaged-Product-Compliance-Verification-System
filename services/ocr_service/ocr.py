import time
from pathlib import Path
from typing import Any, List, Optional, Union
import numpy as np

from backend.utils.logger import logger
from services.ocr_service.image_utils import load_image, ImageValidationError
from services.ocr_service.preprocess import preprocess_image
from services.ocr_service.result import OCRLine, OCRResult


class PaddleOCRService:
    """
    Service wrapper for PaddleOCR engine delivering structured OCR extraction.
    Supports dependency injection of custom/mock engines for testing.
    """

    def __init__(self, ocr_engine: Optional[Any] = None, use_angle_cls: bool = True, lang: str = "en"):
        self._engine = ocr_engine
        self._use_angle_cls = use_angle_cls
        self._lang = lang
        self._initialized = ocr_engine is not None

    def _get_engine(self) -> Any:
        """
        Lazy-loads the PaddleOCR engine on first real invocation.
        """
        if not self._initialized:
            try:
                from paddleocr import PaddleOCR  # type: ignore
                logger.info(f"Initializing PaddleOCR engine (lang={self._lang}, use_angle_cls={self._use_angle_cls})...")
                self._engine = PaddleOCR(
                    use_angle_cls=self._use_angle_cls,
                    lang=self._lang,
                    show_log=False,
                )
                self._initialized = True
                logger.info("PaddleOCR engine initialized successfully.")
            except ImportError as e:
                logger.warning(
                    f"PaddleOCR package is not installed or import failed: {e}. "
                    "Engine must be injected or installed to run non-mocked OCR."
                )
                raise RuntimeError(
                    "PaddleOCR engine is not available. Please install paddleocr and paddlepaddle or inject a mock engine."
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR engine: {e}")
                raise RuntimeError(f"Failed to initialize PaddleOCR: {e}") from e

        return self._engine

    def extract_text(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        preprocess: bool = True,
        strategy: str = "standard",
    ) -> OCRResult:
        """
        Processes an image and returns structured OCR lines, aggregate text, and confidence scores.

        :param image_input: File path, raw bytes, or NumPy RGB array.
        :param preprocess: Whether to apply preprocessing before feeding to OCR engine.
        :param strategy: Preprocessing strategy ('standard', 'grayscale_clahe', 'binarized', 'raw').
        :return: Structured OCRResult.
        """
        start_time = time.perf_counter()

        try:
            # 1. Load and validate image into RGB NumPy array
            image = load_image(image_input)

            # 2. Preprocess if requested
            if preprocess:
                processed_img, _ = preprocess_image(image, strategy=strategy)
            else:
                processed_img = image

            # 3. Execute OCR engine
            engine = self._get_engine()
            raw_ocr_output = engine.ocr(processed_img, cls=self._use_angle_cls)

            # 4. Parse and normalize structured output
            lines: List[OCRLine] = []
            confidence_sum = 0.0

            # PaddleOCR returns a list of results per page: [ [ [box, (text, score)], ... ] ]
            if raw_ocr_output and len(raw_ocr_output) > 0:
                first_page = raw_ocr_output[0]
                if first_page:
                    for item in first_page:
                        if item and len(item) >= 2:
                            box = item[0]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                            text_score = item[1]  # (text_string, score_float)
                            if isinstance(text_score, (list, tuple)) and len(text_score) >= 2:
                                text_str = str(text_score[0]).strip()
                                score_val = float(text_score[1]) if text_score[1] is not None else 0.0

                                if text_str:
                                    lines.append(
                                        OCRLine(
                                            text=text_str,
                                            confidence=round(score_val, 4),
                                            bounding_box=box,
                                        )
                                    )
                                    confidence_sum += score_val

            avg_confidence = round(confidence_sum / len(lines), 4) if lines else 0.0
            full_text = "\n".join(line.text for line in lines)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return OCRResult(
                success=True,
                text=full_text,
                lines=lines,
                average_confidence=avg_confidence,
                processing_time_ms=elapsed_ms,
            )

        except ImageValidationError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return OCRResult(
                success=False,
                text="",
                lines=[],
                average_confidence=0.0,
                error_message=str(e),
                processing_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(f"OCR processing failed: {e}")
            return OCRResult(
                success=False,
                text="",
                lines=[],
                average_confidence=0.0,
                error_message=f"OCR execution error: {str(e)}",
                processing_time_ms=elapsed_ms,
            )


# Default singleton instance
_default_ocr_service: Optional[PaddleOCRService] = None


def get_ocr_service(custom_engine: Optional[Any] = None) -> PaddleOCRService:
    """
    Returns the singleton OCR service instance, or creates one with a custom engine.
    """
    global _default_ocr_service
    if custom_engine is not None:
        return PaddleOCRService(ocr_engine=custom_engine)
    if _default_ocr_service is None:
        _default_ocr_service = PaddleOCRService()
    return _default_ocr_service


def set_ocr_service(service: PaddleOCRService) -> None:
    """
    Sets the global default OCR service (useful for test overrides).
    """
    global _default_ocr_service
    _default_ocr_service = service
