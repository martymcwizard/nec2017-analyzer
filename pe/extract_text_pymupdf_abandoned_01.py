# pe/extract_text_pymupdf.py

import fitz  # PyMuPDF
from .config import HEADER_THRESHOLD_RATIO, FOOTER_THRESHOLD_RATIO

# Validate that the thresholds are between 0 and 1

if not (0 <= HEADER_THRESHOLD_RATIO <= 1):
    raise ValueError("HEADER_THRESHOLD_RATIO must be between 0 and 1.")

if not (0 <= FOOTER_THRESHOLD_RATIO <= 1):
    raise ValueError("FOOTER_THRESHOLD_RATIO must be between 0 and 1.")


def extract_text_excluding_headers_footers(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = []

    #some debug code to verify block type
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        total_blocks = len(blocks)
        print(f"Page {page_num}: Total Blocks = {total_blocks}")
        
        if total_blocks > 0:
            print(f"First block: {blocks[0]}")
            # Optionally, print block_type
            first_block_type = blocks[0][1] if len(blocks[0]) > 1 else 'Unknown'
            print(f"First Block Type: {first_block_type}")
        else:
            print("No blocks found on this page.")
        # For testing, process only the first page
        break



    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        header_threshold = page_height * HEADER_THRESHOLD_RATIO
        footer_threshold = page_height * FOOTER_THRESHOLD_RATIO

        page_text = ''
        blocks = page.get_text("blocks")

        total_blocks = 0
        included_blocks = 0

        for b in blocks:
            rect = b[0]         # The bounding rectangle of the block
            block_type = b[1]   # The type of block (0 = text)
            if block_type != 0:
                continue  # Skip non-text blocks

            text = b[4] if len(b) > 4 else b[2]  # The text content of the block
            x0, y0, x1, y1 = rect


            print(f"Page {page_num}, Block Coordinates: y0={y0}, y1={y1}")
            print(f"Header Threshold: {header_threshold}, Footer Threshold: {footer_threshold}")

            

            # Exclude headers and footers
            if y0 < header_threshold or y1 > footer_threshold:
                continue  # Skip blocks in header or footer areas
            else:
                page_text += text
                included_blocks += 1

        print(f"Page {page_num}: Total Blocks = {total_blocks}, Included Blocks = {included_blocks}")  
        text_content.append(page_text)

    return '\n'.join(text_content)
