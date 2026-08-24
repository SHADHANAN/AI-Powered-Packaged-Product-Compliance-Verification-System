import io
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Tuple, Union
import cv2
import numpy as np
from PIL import Image

# Supported image MIME types and extensions
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
SUPPORTED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/webp",
    "image/tiff",
    "image/x-ms-bmp",
}

# Image validation limits
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
MIN_IMAGE_DIMENSION = 16  # Minimum 16px width/height
MAX_IMAGE_DIMENSION = 10000  # Maximum 10000px width/height


class ImageValidationError(Exception):
    """Raised when uploaded image fails format, size, or integrity validation."""
    pass


def sanitize_filename(filename: Optional[str]) -> str:
    """
    Sanitizes untrusted filenames to prevent directory traversal and special character exploits.
    """
    if not filename:
        return "uploaded_image.jpg"
    # Strip directory components (both Unix and Windows style)
    clean_name = os.path.basename(filename.replace("\\", "/"))
    # Remove null bytes and dangerous control characters
    clean_name = clean_name.replace("\x00", "").strip()
    return clean_name or "uploaded_image.jpg"


def is_valid_extension(filename: str) -> bool:
    """Checks whether the file extension is supported."""
    clean = sanitize_filename(filename)
    ext = Path(clean).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def is_valid_mime_type(mime_type: Optional[str]) -> bool:
    """Checks whether the provided MIME type is supported."""
    if not mime_type:
        return True  # If client did not send MIME, fallback to extension & Pillow header inspection
    clean_mime = mime_type.split(";")[0].strip().lower()
    return clean_mime in SUPPORTED_MIME_TYPES or clean_mime.startswith("image/")


def validate_image_bytes(
    image_bytes: bytes,
    filename: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
    """
    Validates image bytes for size, integrity, and dimensions.
    Returns: (is_valid, error_message, (width, height))
    """
    if not image_bytes or len(image_bytes) == 0:
        return False, "Image file is empty (0 bytes).", None

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        return (
            False,
            f"Image file size ({len(image_bytes) / (1024 * 1024):.2f} MB) exceeds maximum allowed size of {MAX_IMAGE_SIZE_BYTES / (1024 * 1024):.0f} MB.",
            None,
        )

    if filename and not is_valid_extension(filename):
        return (
            False,
            f"Unsupported image format for file '{filename}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            None,
        )

    try:
        # Use Pillow to verify headers and decode image data
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()

        # Re-open after verify() to inspect dimensions and format
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            img_format = img.format

            if img_format and img_format.lower() not in {"jpeg", "png", "bmp", "webp", "tiff", "mpo"}:
                return False, f"Unsupported image encoding format: {img_format}", None

            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                return (
                    False,
                    f"Image dimensions ({width}x{height}) are too small. Minimum dimension is {MIN_IMAGE_DIMENSION}px.",
                    None,
                )

            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                return (
                    False,
                    f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of {MAX_IMAGE_DIMENSION}px.",
                    None,
                )

            return True, None, (width, height)

    except Exception as e:
        return False, f"Corrupted or unreadable image data: {str(e)}", None


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decodes image bytes into a standard RGB NumPy array (OpenCV format converted to RGB).
    Raises ImageValidationError if image decoding fails.
    """
    is_valid, error_msg, _ = validate_image_bytes(image_bytes)
    if not is_valid:
        raise ImageValidationError(error_msg or "Invalid image data.")

    # Convert bytes to numpy array for cv2 decoding
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image_bgr is None:
        # Fallback to Pillow if OpenCV imdecode failed
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return np.array(pil_img)
        except Exception as e:
            raise ImageValidationError(f"Failed to decode image: {str(e)}")

    # Convert BGR to RGB
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def load_image_from_path(file_path: Union[str, Path]) -> np.ndarray:
    """
    Reads an image from a filesystem path into an RGB NumPy array.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    with open(path, "rb") as f:
        image_bytes = f.read()

    return load_image_from_bytes(image_bytes)


def load_image(source: Union[str, Path, bytes, np.ndarray, Image.Image]) -> np.ndarray:
    """
    Universal image loader accepting file paths, bytes, NumPy arrays, or PIL Images.
    Returns RGB NumPy array.
    """
    if isinstance(source, np.ndarray):
        if len(source.shape) == 2:
            return cv2.cvtColor(source, cv2.COLOR_GRAY2RGB)
        elif len(source.shape) == 3 and source.shape[2] == 4:
            return cv2.cvtColor(source, cv2.COLOR_RGBA2RGB)
        return source

    if isinstance(source, Image.Image):
        return np.array(source.convert("RGB"))

    if isinstance(source, (str, Path)):
        return load_image_from_path(source)

    if isinstance(source, bytes):
        return load_image_from_bytes(source)

    raise ValueError(f"Unsupported image source type: {type(source)}")


@contextmanager
def temp_image_file(image_bytes: bytes, suffix: str = ".jpg") -> Generator[Path, None, None]:
    """
    Context manager that safely writes image bytes to a temporary file and guarantees cleanup.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = Path(temp_file.name)
    try:
        temp_file.write(image_bytes)
        temp_file.flush()
        temp_file.close()
        yield temp_path
    finally:
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except OSError:
                pass
