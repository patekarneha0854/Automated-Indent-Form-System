import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_mmd_pdf(indent_data, output_filename="generated_forms/MMD_Indent_Form.pdf"):
    """
    Generates an official MMD (Materials Management Division) Indent Form PDF.
    
    Parameters:
    indent_data (dict): Contains user input, department details, and list of selected items.
    output_filename (str): The file path where the generated PDF will be saved locally.
    
    Returns:
    str: The file path of the successfully generated PDF.
    """
    # Ensure the output directory exists before attempting to save the file
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Initialize the PDF document with Letter page size and standard 0.5-inch margins
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    # List to hold all the flowable elements (paragraphs, tables, spacers) of the PDF document
    story = []
    
    # Retrieve default stylesheet from ReportLab to base our custom styles on
    styles = getSampleStyleSheet()
    
    # Define custom professional paragraph styles for headings, subheadings, and regular body text
    title_style = ParagraphStyle(
        'MMDTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        alignment=1, # Center alignment
        textColor=colors.HexColor("#1A365D") # Professional Navy Blue
    )
    
    subtitle_style = ParagraphStyle(
        'MMDSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#4A5568") # Slate Grey
    )
    
    cell_style = ParagraphStyle(
        'MMDCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    
    header_cell_style = ParagraphStyle(
        'MMDHeaderCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    # --- Header Section ---
    story.append(Paragraph("INSTITUTIONAL PROCUREMENT SYSTEM", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("MATERIALS MANAGEMENT DIVISION (MMD) - INDENT FORM", title_style))
    story.append(Spacer(1, 10))
    
    # --- Department & Requester Metadata Table ---
    meta_data = [
        [Paragraph("<b>Department:</b> " + indent_data.get('department', 'N/A'), cell_style),
         Paragraph("<b>Date:</b> " + indent_data.get('date', 'N/A'), cell_style)],
        [Paragraph("<b>Requester Name:</b> " + indent_data.get('requester', 'N/A'), cell_style),
         Paragraph("<b>Indent ID:</b> " + indent_data.get('indent_id', 'IND-MMD-001'), cell_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # --- Items Table Header & Rows Construction ---
    table_data = [[
        Paragraph("Sr. No.", header_cell_style),
        Paragraph("Item Name & Description", header_cell_style),
        Paragraph("Model / Part No.", header_cell_style),
        Paragraph("Qty", header_cell_style),
        Paragraph("Unit Price (₹)", header_cell_style),
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
            Paragraph(f"{item.get('model', 'N/A')}<br/>{item.get('part_number', '')}", cell_style),
            Paragraph(str(qty), cell_style),
            Paragraph(f"{unit_price:,.2f}", cell_style),
            Paragraph(f"{total_price:,.2f}", cell_style)
        ]
        table_data.append(row)
        
    # Append Grand Total Row
    table_data.append([
        Paragraph("<b>Grand Total</b>", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph(f"<b>₹{grand_total:,.2f}</b>", cell_style)
    ])
    
    # Build main items table with explicit column widths matching letter width constraints
    col_widths = [40, 180, 110, 40, 90, 80]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")), # Navy blue header background
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#A0AEC0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, -1), (4, -1)), # Span columns for Grand Total label row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EDF2F7")), # Light grey highlight for total row
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # --- Purpose & Justification Section ---
    purpose_text = f"<b>Purpose / Justification:</b> {indent_data.get('purpose', 'Standard institutional requirements.')}"
    story.append(Paragraph(purpose_text, cell_style))
    story.append(Spacer(1, 40))
    
    # --- Signatures Section ---
    sig_data = [
        [Paragraph("<b>Prepared By</b><br/><br/><br/>________________________<br/>Signature & Date", cell_style),
         Paragraph("<b>HOD / Department Head</b><br/><br/><br/>________________________<br/>Signature & Stamp", cell_style),
         Paragraph("<b>MMD Officer</b><br/><br/><br/>________________________<br/>Approved / Sanctioned", cell_style)]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(sig_table)
    
    # Build and write the PDF document
    doc.build(story)
    return output_filename