from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

def make_pdf(title, rows):
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4)
    styles=getSampleStyleSheet()
    story=[Paragraph(title,styles["Title"]),Spacer(1,14),
           Paragraph("Educational prototype report. Not an official forecast or emergency instruction.",styles["BodyText"]),Spacer(1,12),
           Table([["Metric","Value"]]+[[str(k),str(v)] for k,v in rows],repeatRows=1)]
    doc.build(story); buffer.seek(0); return buffer
