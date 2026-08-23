import cv2
import numpy as np
from typing import Dict, Tuple, Optional


def resize_image(
    image: np.ndarray,
    max_dimension: int = 2500,
    min_dimension: int = 600,
) -> Tuple[np.ndarray, float]:
    """
    Resizes image to stay within optimal bounds while strictly preserving aspect ratio.
    Returns: (resized_image, scale_factor)
    """
    height, width = image.shape[:2]
    max_side = max(height, width)
    min_side = min(height, width)

    scale = 1.0

    # Scale down if too large (improves OCR speed and memory usage)
    if max_side > max_dimension:
        scale = max_dimension / float(max_side)
    # Scale up if too small (improves character recognition on low-res labels)
    elif min_side < min_dimension:
        scale = min_dimension / float(min_side)

    if scale != 1.0:
        new_width = int(round(width * scale))
        new_height = int(round(height * scale))
        interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
        resized = cv2.resize(image, (new_width, new_height), interpolation=interpolation)
        return resized, scale

    return image.copy(), 1.0


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Converts RGB/BGR image to single-channel grayscale.
    """
    if len(image.shape) == 2:
        return image.copy()
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def enhance_contrast(
    gray_image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
    to boost localized text clarity on shiny or unevenly lit packaging.
    """
    if len(gray_image.shape) == 3:
        gray = to_grayscale(gray_image)
    else:
        gray = gray_image

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)


def reduce_noise(
    image: np.ndarray,
    method: str = "bilateral",
    d: int = 7,
    sigma_color: float = 50.0,
    sigma_space: float = 50.0,
) -> np.ndarray:
    """
    Reduces grain and compression noise while strictly preserving sharp text edges.
    """
    if method == "bilateral":
        return cv2.bilateralFilter(image, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)
    elif method == "gaussian":
        return cv2.GaussianBlur(image, (3, 3), 0)
    elif method == "median":
        return cv2.medianBlur(image, 3)
    return image.copy()


def binarize(
    gray_image: np.ndarray,
    method: str = "otsu",
) -> np.ndarray:
    """
    Converts grayscale image to binary black & white for extreme contrast.
    """
    if len(gray_image.shape) == 3:
        gray = to_grayscale(gray_image)
    else:
        gray = gray_image

    if method == "otsu":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    elif method == "adaptive":
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    return gray


def deskew_image(gray_image: np.ndarray, max_angle: float = 15.0) -> Tuple[np.ndarray, float]:
    """
    Detects slight rotation angle on packaging and straightens the text.
    Returns: (deskewed_image, angle_degrees)
    """
    if len(gray_image.shape) == 3:
        gray = to_grayscale(gray_image)
    else:
        gray = gray_image

    coords = np.column_stack(np.where(gray < 250))
    if coords.size == 0:
        return gray.copy(), 0.0

    angle = 0.0
    try:
        min_rect = cv2.minAreaRect(coords)
        rect_angle = min_rect[-1]
        if rect_angle < -45:
            angle = -(90 + rect_angle)
        elif rect_angle > 45:
            angle = 90 - rect_angle
        else:
            angle = -rect_angle

        if abs(angle) > max_angle or abs(angle) < 0.5:
            return gray.copy(), 0.0

        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            gray,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rotated, angle
    except Exception:
        return gray.copy(), 0.0


def preprocess_image(
    image: np.ndarray,
    strategy: str = "standard",
) -> Tuple[np.ndarray, Dict[str, any]]:
    """
    Modular pipeline applying pre-processing strategies for OCR extraction.
    Strategies:
      - 'standard': Safe resize + mild noise reduction + contrast preservation (preserves RGB for PaddleOCR).
      - 'grayscale_clahe': Resize + Grayscale + CLAHE + Denoise.
      - 'binarized': Resize + Grayscale + CLAHE + Otsu Thresholding.
      - 'raw': Passthrough without modification.

    Returns: (processed_image, metadata)
    """
    meta: Dict[str, any] = {"strategy": strategy, "original_shape": image.shape}

    if strategy == "raw":
        return image.copy(), meta

    # Step 1: Resize
    resized, scale = resize_image(image)
    meta["scale_factor"] = scale
    meta["resized_shape"] = resized.shape

    if strategy == "standard":
        # Mild bilateral filtering to suppress background label noise while retaining crisp font edges
        denoised = reduce_noise(resized, method="bilateral", d=5, sigma_color=30.0, sigma_space=30.0)
        return denoised, meta

    elif strategy == "grayscale_clahe":
        gray = to_grayscale(resized)
        enhanced = enhance_contrast(gray, clip_limit=2.0)
        denoised = reduce_noise(enhanced, method="bilateral", d=5)
        return denoised, meta

    elif strategy == "binarized":
        gray = to_grayscale(resized)
        enhanced = enhance_contrast(gray, clip_limit=2.0)
        binary = binarize(enhanced, method="otsu")
        return binary, meta

    # Fallback to resized
    return resized, meta
