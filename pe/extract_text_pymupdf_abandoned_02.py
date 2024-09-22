# pe/extract_text_pymupdf.py

import fitz  # PyMuPDF
from .config import HEADER_THRESHOLD_RATIO, FOOTER_THRESHOLD_RATIO

def extract_text_excluding_headers_footers(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = []

    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        header_threshold = page_height * HEADER_THRESHOLD_RATIO
        footer_threshold = page_height * FOOTER_THRESHOLD_RATIO

        page_text = ''
        blocks = page.get_text("blocks")
        total_blocks = len(blocks)
        included_blocks = 0

        print(f"Page {page_num}: Total Blocks = {total_blocks}")

        for b in blocks[2:-1]:
            # Correctly unpack the block tuple
            x0, y0, x1, y1, text, block_no, block_type = b
    

            # Exclude headers and footers
            if y0 < header_threshold or y1 > footer_threshold:
                continue  # Skip blocks in header or footer areas

            # Process only text blocks
            #if block_type != 0:
            #    continue
            print(f"Block No {block_no}: Block Type = {block_type}")

            page_text += text
            included_blocks += 1

        print(f"Page {page_num}: Included Blocks = {included_blocks}")
        text_content.append(page_text)

    return '\n'.join(text_content)
