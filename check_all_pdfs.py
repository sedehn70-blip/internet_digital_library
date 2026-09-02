import fitz  # PyMuPDF
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = Path(r"g:\digital_library1\uploads\books\pdf")

print("Checking all PDFs for encoding issues...")
print("="*50)

for pdf_path in pdf_dir.glob("*.pdf"):
    if "_fixed" in pdf_path.name:
        continue
    
    print(f"\n--- {pdf_path.name} ---")
    
    try:
        doc = fitz.open(pdf_path)
        
        # Check first 2 pages
        has_issue = False
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
                                has_issue = True
                                print(f"  - Found garbled text with font: {font}")
                                print(f"  - Sample: {text[:50]}")
                                break
                        if has_issue:
                            break
                    if has_issue:
                        break
            if has_issue:
                break
        
        if not has_issue:
            print("  - No encoding issues detected")
        
        doc.close()
        
    except Exception as e:
        print(f"  - Error: {e}")

print("\n" + "="*50)
