# func/pdf_processing.py

import fitz  # PyMuPDF
import pdfplumber
from pdfplumber.utils import extract_text, get_bbox_overlap, obj_to_bbox
from io import BytesIO

# def extract_text_from_pdf(uploaded_file):
#     """Extracts text from an uploaded PDF file."""
#     text = ""
#     # Use BytesIO to handle in-memory file
#     pdf_data = BytesIO(uploaded_file.read())
#     with fitz.open(stream=pdf_data, filetype="pdf") as doc:
#         for page in doc:
#             text += page.get_text()
#     return text

def extract_text_from_pdf(uploaded_file):
    pdf = pdfplumber.open(BytesIO(uploaded_file.read()),strict_metadata=True)
    all_text = []

    for page in pdf.pages:
        filtered_page = page
        chars = filtered_page.chars

        for table in page.find_tables():
          try:
            first_table_char = page.crop(table.bbox).chars[0]
            filtered_page = filtered_page.filter(lambda obj: 
                get_bbox_overlap(obj_to_bbox(obj), table.bbox) is None
            )
            chars = filtered_page.chars

            df = pd.DataFrame(table.extract())
            df.columns = df.iloc[0]
            markdown = df.drop(0).to_markdown(index=False)

            chars.append(first_table_char | {"text": markdown})
          except:
            pass

        page_text = extract_text(chars, layout=True).encode('utf-8').decode('latin-1')
        all_text.append(page_text)

    pdf.close()
    return "\n".join(all_text)