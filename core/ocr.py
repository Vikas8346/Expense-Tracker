import cv2
import pytesseract
from PIL import Image
import numpy as np
import os

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

        return text.strip()

    except Exception as e:
        print(f"OCR Error: {e}")
        # Fallback: try OCR on original image
        try:
            text = pytesseract.image_to_string(image_path)
            return text.strip()
        except:
            return ""

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
