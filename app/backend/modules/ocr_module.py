"""
MODULE 1: OCR Module

Conditional preprocessing of FIR text.
- If input is text: return unchanged
- If input is image path: extract using pytesseract
- Graceful fallback if pytesseract unavailable
"""

import logging
from pathlib import Path

logger = logging.getLogger("byomkesh.ocr")


class OCRModule:
    """Preprocessor for FIR intake: text passthrough or image extraction."""

    def __init__(self):
        self.pytesseract_available = self._check_pytesseract()

    def _check_pytesseract(self) -> bool:
        """Check if pytesseract is installed and accessible."""
        try:
            import pytesseract
            from PIL import Image
            return True
        except ImportError:
            logger.warning("pytesseract or Pillow not installed; image OCR unavailable")
            return False

    def process(self, input_data: str, input_type: str = "text") -> tuple[str, bool]:
        """
        Process input data — either text passthrough or image OCR.

        Args:
            input_data: raw text or path to image file
            input_type: "text" or "image_path"

        Returns:
            (extracted_text, ocr_applied: bool)
        """
        if input_type == "text":
            logger.info("[OCR] input_type=text, ocr_applied=False")
            return input_data, False

        if input_type == "image_path":
            if not self.pytesseract_available:
                logger.warning(
                    "[OCR] pytesseract unavailable; returning original input"
                )
                return input_data, False

            try:
                import pytesseract
                from PIL import Image

                image_path = Path(input_data)
                if not image_path.exists():
                    logger.error(f"[OCR] Image not found: {input_data}")
                    return input_data, False

                image = Image.open(image_path)
                extracted = pytesseract.image_to_string(image)

                if not extracted.strip():
                    logger.warning("[OCR] No text extracted from image; using fallback")
                    return input_data, False

                logger.info(
                    f"[OCR] image_path={input_data}, ocr_applied=True, "
                    f"chars_extracted={len(extracted)}"
                )
                return extracted, True

            except Exception as e:
                logger.error(f"[OCR] image processing failed: {e}; using fallback")
                return input_data, False

        # Unknown input_type
        logger.warning(f"[OCR] unknown input_type={input_type}; returning input unchanged")
        return input_data, False
