import fitz  # PyMuPDF
import easyocr
from pathlib import Path
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OCR reader (lazy loading)
_reader = None

def get_ocr_reader():
    """Get or create OCR reader instance"""
    global _reader
    if _reader is None:
        try:
            _reader = easyocr.Reader(['fa', 'en'], gpu=False)
            logger.info("EasyOCR reader initialized")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            return None
    return _reader

def has_encoding_issue(pdf_path):
    """Check if PDF has encoding issues with Persian text"""
    try:
        doc = fitz.open(pdf_path)
        
        # Check first 2 pages for garbled Persian characters
        for page_num in range(min(2, len(doc))):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            blocks = text_dict.get("blocks", [])
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font = span.get("font", "")
                            text = span.get("text", "")
                            # Check for garbled Persian characters
                            if text.strip() and any(c in text for c in ['Ȃ', 'Ɛ', 'Ɖ', 'ȁ', 'Ȋ', 'Ľ', 'ȋ', 'ȅ']):
                                doc.close()
                                return True
        
        doc.close()
        return False
    except Exception as e:
        logger.error(f"Error checking encoding: {e}")
        return False

def fix_pdf_encoding(pdf_path, output_path=None):
    """
    Fix PDF encoding issues by using OCR to extract correct Persian text
    and creating a new PDF with searchable text layer.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path for the fixed PDF (if None, overwrites original)
    
    Returns:
        Path to the fixed PDF, or None if failed
    """
    if output_path is None:
        output_path = pdf_path
    
    try:
        reader = get_ocr_reader()
        if reader is None:
            logger.warning("OCR not available, skipping fix")
            return None
        
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            logger.info(f"Processing page {page_num + 1}/{len(doc)}")
            
            # Render page to image for OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            
            # Extract text using OCR
            result = reader.readtext(img_data)
            
            # Combine all detected text
            full_text = ""
            for (bbox, text, confidence) in result:
                if confidence > 0.5:
                    full_text += text + "\n"
            
            # Create new page with same dimensions
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Insert the image
            new_page.insert_image(new_page.rect, stream=img_data)
            
            # Add OCR text as invisible layer for searchability
            if full_text.strip():
                new_page.insert_text(
                    fitz.Point(50, 50),
                    full_text,
                    fontsize=1,  # Very small, nearly invisible
                    color=(1, 1, 1)  # White (invisible on white background)
                )
            
            logger.info(f"  - Extracted {len(full_text)} characters")
        
        # Save the new PDF
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        logger.info(f"Fixed PDF saved to: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error fixing PDF: {e}")
        return None

def process_pdf_on_upload(pdf_path):
    """
    Process PDF after upload - check for encoding issues and fix if needed.
    This is intended to be called during the upload process.
    
    Args:
        pdf_path: Path to the uploaded PDF file
    
    Returns:
        True if PDF was processed (fixed or no issues), False if failed
    """
    try:
        # Check if PDF has encoding issues
        if has_encoding_issue(pdf_path):
            logger.info(f"Encoding issue detected in {pdf_path}, attempting to fix...")
            result = fix_pdf_encoding(pdf_path)
            if result:
                logger.info(f"Successfully fixed PDF: {pdf_path}")
                return True
            else:
                logger.warning(f"Failed to fix PDF: {pdf_path}")
                return False
        else:
            logger.info(f"No encoding issues in {pdf_path}")
            return True
    except Exception as e:
        logger.error(f"Error processing PDF on upload: {e}")
        return False

if __name__ == "__main__":
    # Test on a specific PDF
    test_pdf = r"g:\digital_library1\uploads\books\pdf\9c15cccb681947388151eace175e0819_110.pdf"
    if has_encoding_issue(test_pdf):
        print("Encoding issue detected, fixing...")
        fix_pdf_encoding(test_pdf)
    else:
        print("No encoding issues")
