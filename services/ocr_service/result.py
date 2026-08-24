from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any


@dataclass
class OCRLine:
    """
    Represents a single recognized text line with bounding box and confidence.
    """
    text: str
    confidence: float
    bounding_box: Optional[List[List[float]]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OCRResult:
    """
    Structured outcome of an OCR operation on an image.
    """
    success: bool
    text: str
    lines: List[OCRLine] = field(default_factory=list)
    average_confidence: float = 0.0
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "text": self.text,
            "lines": [line.to_dict() for line in self.lines],
            "average_confidence": round(self.average_confidence, 4),
            "error_message": self.error_message,
            "processing_time_ms": round(self.processing_time_ms, 2) if self.processing_time_ms is not None else None,
        }
