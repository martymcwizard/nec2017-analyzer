# pe/extract_text_pymupdf.py

import fitz  # PyMuPDF
from itertools import islice
import re

def extract_text_excluding_headers_footers(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = []

    for page_num, page in enumerate(islice(doc, 32, 38), start=33):

        page_text = ''
        blocks = page.get_text("blocks")
        #total_blocks = len(blocks)
        #included_blocks = 0

        #print(f"Page {page_num}: Total Blocks = {total_blocks}")

        for b in blocks[1:]:
            # Correctly unpack the block tuple
            x0, y0, x1, y1, text, block_no, block_type = b

            # Apply logic only to block 1
            if block_no == 1:
                #print(f"Block 1 Text: {text}")
 
                # Normalize the en dash to a hyphen and remove leading/trailing whitespace
                text = text.replace('\u2013', '-').replace('\u2014', '-')  # Replace en and em dash with hyphen
                text = text.strip()  # Remove leading/trailing whitespace

                # Now check for the page number with the normalized hyphen
                page_number_match = re.search(r'70 -\d{2,3}', text)

                #print(f"what matched: {page_number_match}")
                if page_number_match:
                    # Append the formatted page number
                    page_text += "PAGE NUMBER " + page_number_match.group(0) + "\n"
                # Skip adding the redundant footer
                continue
    
            page_text += text
            #included_blocks += 1

        #print(f"Page {page_num}: Included Blocks = {included_blocks}")
        text_content.append(page_text)

    return '\n'.join(text_content)
