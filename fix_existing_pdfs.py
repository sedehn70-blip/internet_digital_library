from pdf_encoding_fixer import has_encoding_issue, fix_pdf_encoding
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = Path(r"g:\digital_library1\uploads\books\pdf")

print("Fixing existing PDFs with encoding issues...")
print("="*50)

fixed_count = 0
failed_count = 0

for pdf_path in pdf_dir.glob("*.pdf"):
    if "_fixed" in pdf_path.name:
        continue
    
    print(f"\n--- Checking {pdf_path.name} ---")
    
    try:
        if has_encoding_issue(str(pdf_path)):
            print(f"  - Encoding issue detected, fixing...")
            result = fix_pdf_encoding(str(pdf_path))
            if result:
                print(f"  - Successfully fixed!")
                fixed_count += 1
            else:
                print(f"  - Failed to fix")
                failed_count += 1
        else:
            print(f"  - No encoding issues")
    except Exception as e:
        print(f"  - Error: {e}")
        failed_count += 1

print("\n" + "="*50)
print(f"Summary: {fixed_count} fixed, {failed_count} failed")
