import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_rd_pdf(indent_data, output_filename="generated_forms/RD_Indent_Form.pdf"):
    """
    Generates an official R&D (Research & Development) Indent Form PDF with research grant considerations.
    
    Parameters:
    indent_data (dict): Contains user input, research project details, grant info, and items.
    output_filename (str): The file path where the generated PDF will be saved locally.
    
    Returns:
    str: The file path of the successfully generated PDF.
    """
    # Ensure the output directory exists before writing the PDF file
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Initialize the PDF document layout
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles tailored for R&D indent format (Using Deep Forest Green accent for Research)
    title_style = ParagraphStyle(
        'RDTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#22543D") # Deep Forest Green
    )
    
    subtitle_style = ParagraphStyle(
        'RDSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#2F855A")
    )
    
    cell_style = ParagraphStyle(
        'RDCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    
    header_cell_style = ParagraphStyle(
        'RDHeaderCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    # --- Header Section ---
    story.append(Paragraph("RESEARCH & DEVELOPMENT DIVISION", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("SPECIALIZED R&D EQUIPMENT INDENT FORM", title_style))
    story.append(Spacer(1, 10))
    
    # --- Project & Grant Metadata Table ---
    meta_data = [
        [Paragraph("<b>Research Lab / Dept:</b> " + indent_data.get('department', 'N/A'), cell_style),
         Paragraph("<b>Date:</b> " + indent_data.get('date', 'N/A'), cell_style)],
        [Paragraph("<b>Principal Investigator (PI):</b> " + indent_data.get('requester', 'N/A'), cell_style),
         Paragraph("<b>Project / Grant Code:</b> " + indent_data.get('grant_code', 'INST-RD-GRANT'), cell_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#9AE6B4")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#C6F6D5")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # --- Equipment Items Table ---
    table_data = [[
        Paragraph("Sr. No.", header_cell_style),
        Paragraph("Equipment & Technical Specs", header_cell_style),
        Paragraph("Make / Model", header_cell_style),
        Paragraph("Qty", header_cell_style),
        Paragraph("Approx. Unit (₹)", header_cell_style),
        Paragraph("Total (₹)", header_cell_style)
    ]]
    
    items = indent_data.get('items', [])
    grand_total = 0.0
    
    for idx, item in enumerate(items, 1):
        qty = item.get('quantity', 1)
        unit_price = item.get('unit_price', 0.0)
        total_price = qty * unit_price
        grand_total += total_price
        
        row = [
            Paragraph(str(idx), cell_style),
            Paragraph(f"<b>{item.get('item_name')}</b><br/>{item.get('description', '')}", cell_style),
            Paragraph(f"{item.get('manufacturer', 'N/A')}<br/>{item.get('model', 'N/A')}", cell_style),
            Paragraph(str(qty), cell_style),
            Paragraph(f"{unit_price:,.2f}", cell_style),
            Paragraph(f"{total_price:,.2f}", cell_style)
        ]
        table_data.append(row)
        
    # Grand Total Row
    table_data.append([
        Paragraph("<b>Estimated Grand Total</b>", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph(f"<b>₹{grand_total:,.2f}</b>", cell_style)
    ])
    
    col_widths = [40, 180, 110, 40, 90, 80]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#22543D")), # Forest green header background
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#38A169")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#9AE6B4")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, -1), (4, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F0FFF4")), # Light green highlight for total row
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # --- Technical Justification Section ---
    purpose_text = f"<b>Research Justification & Experiment Utility:</b> {indent_data.get('purpose', 'Required for advanced lab experiments and research validation.')}"
    story.append(Paragraph(purpose_text, cell_style))
    story.append(Spacer(1, 40))
    
    # --- Signatures Section ---
    sig_data = [
        [Paragraph("<b>Researcher / Applicant</b><br/><br/><br/>________________________<br/>Signature & Date", cell_style),
         Paragraph("<b>Principal Investigator (PI)</b><br/><br/><br/>________________________<br/>Signature & Seal", cell_style),
         Paragraph("<b>Dean R&D / Director</b><br/><br/><br/>________________________<br/>Sanctioned / Approved", cell_style)]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(sig_table)
    
    # Build and finalize the PDF file
    doc.build(story)
    return output_filename