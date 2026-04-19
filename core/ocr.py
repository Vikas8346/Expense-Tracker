import cv2
import pytesseract
from PIL import Image
import numpy as np
import os
import shutil
import sys

# Configure pytesseract to use Tesseract installation
# Standard Windows installation path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Check if Tesseract is installed
TESSERACT_AVAILABLE = False
TESSERACT_CMD = None

def check_tesseract():
    """Check if Tesseract is installed and accessible."""
    global TESSERACT_AVAILABLE, TESSERACT_CMD

    # Try standard Windows path first
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH
        TESSERACT_CMD = TESSERACT_PATH
        TESSERACT_AVAILABLE = True
        print(f"✓ Tesseract found at: {TESSERACT_PATH}")
        return True

    # Common Windows installation paths
    paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\%s\AppData\Local\Tesseract-OCR\tesseract.exe" % os.getenv('USERNAME'),
    ]

    # Check environment variable
    env_path = os.getenv('TESSERACT_CMD')
    if env_path:
        paths.insert(0, env_path)

    # Try to find tesseract in PATH
    try:
        if shutil.which('tesseract'):
            TESSERACT_AVAILABLE = True
            return True
    except:
        pass

    # Check specified paths
    for path in paths:
        if os.path.exists(path):
            TESSERACT_CMD = path
            pytesseract.pytesseract.pytesseract_cmd = path
            TESSERACT_AVAILABLE = True
            print(f"✓ Tesseract found at: {path}")
            return True

    print("✗ Tesseract not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

# Check on module load
check_tesseract()

def preprocess_image(image_path):
    """
    Preprocess receipt image for better OCR accuracy.
    - Convert to grayscale
    - Denoise
    - Apply threshold
    - Deskew if needed
    """
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # Apply bilateral filter for better text preservation
    bilateral = cv2.bilateralFilter(denoised, 11, 17, 17)

    # Apply adaptive threshold for better text contrast
    thresh = cv2.adaptiveThreshold(bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # Apply morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return morph

def extract_text_from_receipt(image_path):
    """
    Extract text from receipt image using Tesseract OCR.
    First preprocesses the image for better accuracy.
    """
    if not TESSERACT_AVAILABLE:
        raise RuntimeError(
            "Tesseract OCR is not installed. Please install it from: "
            "https://github.com/UB-Mannheim/tesseract/wiki\n"
            "Installation instructions:\n"
            "1. Download tesseract-ocr-w64-setup-vX.X.X.exe\n"
            "2. Run installer with default path: C:\\Program Files\\Tesseract-OCR\n"
            "3. Restart your terminal\n"
            "4. Run: tesseract --version to verify"
        )

    try:
        # Preprocess image
        processed = preprocess_image(image_path)

        # Save processed image temporarily
        temp_path = image_path.replace('.', '_processed.')
        cv2.imwrite(temp_path, processed)

        # Extract text using Tesseract
        text = pytesseract.image_to_string(temp_path, config='--psm 6')

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not text.strip():
            raise ValueError("No text could be extracted from image")

        return text.strip()

    except pytesseract.TesseractNotFoundError as e:
        print(f"Tesseract Not Found: {e}")
        raise RuntimeError(
            "Tesseract OCR is not installed or not in PATH.\n"
            "Please install from: https://github.com/UB-Mannheim/tesseract/wiki"
        )
    except Exception as e:
        print(f"OCR Error: {e}")
        # Fallback: try OCR on original image
        try:
            text = pytesseract.image_to_string(image_path)
            if text.strip():
                return text.strip()
            else:
                raise ValueError("Could not extract text from receipt image")
        except Exception as fallback_error:
            print(f"Fallback OCR also failed: {fallback_error}")
            raise RuntimeError(
                f"Could not extract text from receipt. Error: {str(fallback_error)}\n"
                "Make sure Tesseract is installed and receipt is clear."
            )

def extract_from_pdf(pdf_path):
    """
    Extract images from PDF and process them.
    Returns concatenated OCR text from all pages.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        all_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality

            # Save page as temp image
            temp_img = f"temp_page_{page_num}.png"
            pix.save(temp_img)

            # Extract text
            text = extract_text_from_receipt(temp_img)
            if text:
                all_text.append(text)

            # Clean up
            if os.path.exists(temp_img):
                os.remove(temp_img)

        doc.close()
        return " ".join(all_text)

    except ImportError:
        return ""
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
