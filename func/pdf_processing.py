# func/pdf_processing.py

import pdfplumber
import pandas as pd
from pdfplumber.utils import extract_text, get_bbox_overlap, obj_to_bbox
from io import BytesIO
from fpdf import FPDF

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

def generate_pdf(text):
    # Remove Non-Unicode font 
    text = text.replace('’','').replace('—','-').replace('≈','=').replace('“','"').replace('–','-').replace('”','"')

    pdf = FPDF(orientation='P', #Portrait
               unit= 'in', #inches
               format='A4' #A4 Page
               )
    
    # Document Layout & Content
    pdf.add_page()
    pdf.set_font('Times',style="BI", size=18)
    pdf.cell(w=7, h=0.25, text = "Candidate Assessment", align = 'C')
    pdf.ln()
    pdf.ln()
    pdf.ln()
    pdf.set_font('Times',style="", size=12)
    pdf.multi_cell(w=7, h=0.25, align="J", text=f"{text}",markdown=True)
    pdf.cell(w=7, h=0.25, text=f"Regards,",markdown=True, align = 'L')
    pdf.ln()
    pdf.cell(w=7, h=0.25, text=f"Talent Acquisition & Development.",markdown=True)

    # Save PDF to an in-memory buffer
    return BytesIO(pdf.output())