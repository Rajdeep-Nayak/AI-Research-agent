from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Autonomous Research Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(text, filename="research_report.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Handle unicode/latin-1 issues by replacing common problem characters
    # (FPDF is simple and sometimes struggles with emojis/special chars)
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 10, safe_text)
    
    # Ensure directory exists
    os.makedirs("downloads", exist_ok=True)
    output_path = f"downloads/{filename}"
    pdf.output(output_path)
    return output_path