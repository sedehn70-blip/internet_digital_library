import easyocr
import fitz  # PyMuPDF
from pathlib import Path
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"g:\digital_library1\uploads\books\pdf\9c15cccb681947388151eace175e0819_110.pdf"
output_path = r"g:\digital_library1\uploads\books\pdf\9c15cccb681947388151eace175e0819_110_fixed.pdf"
images_dir = Path(r"g:\digital_library1\pdf_images")

print("Processing all pages with EasyOCR and creating fixed PDF...")
print("="*50)

try:
    # Initialize EasyOCR reader with Persian and English
    reader = easyocr.Reader(['fa', 'en'], gpu=False)
    
    # Open original PDF
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()
    
    # Process all pages
    image_files = sorted(images_dir.glob("page_*.png"))
    
    for idx, img_path in enumerate(image_files):
        page_num = idx
        page = doc[page_num]
        
        print(f"Processing page {page_num + 1}/{len(doc)}...")
        
        # Extract text using EasyOCR
        result = reader.readtext(str(img_path))
        
        # Combine all detected text
        full_text = ""
        for (bbox, text, confidence) in result:
            if confidence > 0.5:
                full_text += text + "\n"
        
        # Render page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        
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
        
        print(f"  - Extracted {len(full_text)} characters")
    
    # Save the new PDF
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    
    print("\n" + "="*50)
    print(f"Fixed PDF saved to: {output_path}")
    print("The PDF now has searchable Persian text extracted via OCR.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
