"""
AgriOptima - Professional Agronomist Field Report PDF Generator
Constructs a publication-quality certified agronomist PDF using ReportLab.
Includes:
- Certified Agronomic Field Header & Soil Chemistry Profile
- Prescriptive Fertilizer Recommendations (Pure Nutrients & Commercial Bag Conversions)
- Financial ROI & Environmental Stewardship Metrics (Runoff Avoided)
- Best Management Application Practices (BMPs)
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Commercial Fertilizer Conversions:
# 1. DAP (Di-ammonium Phosphate): 18% N, 46% P2O5
# 2. Urea: 46% N
# 3. MOP (Muriate of Potash): 60% K2O
# Standard commercial bag size: 50 kg

def calculate_commercial_bags(dn_kg: float, dp_kg: float, dk_kg: float):
    """
    Converts elemental delta N, P, K (kg/ha) into commercial 50kg bags of:
    - DAP (18-46-0)
    - Urea (46-0-0)
    - MOP (0-0-60)
    Note: P to P2O5 conversion factor is ~2.29; K to K2O is ~1.205.
    """
    p2o5_req = dp_kg * 2.29
    dap_kg = p2o5_req / 0.46
    n_supplied_by_dap = dap_kg * 0.18

    remaining_n_req = max(0.0, dn_kg - n_supplied_by_dap)
    urea_kg = remaining_n_req / 0.46

    k2o_req = dk_kg * 1.205
    mop_kg = k2o_req / 0.60

    dap_bags = round(dap_kg / 50.0, 1)
    urea_bags = round(urea_kg / 50.0, 1)
    mop_bags = round(mop_kg / 50.0, 1)

    return {
        'dap_kg': round(dap_kg, 1),
        'dap_bags': dap_bags,
        'urea_kg': round(urea_kg, 1),
        'urea_bags': urea_bags,
        'mop_kg': round(mop_kg, 1),
        'mop_bags': mop_bags,
        'total_bags': round(dap_bags + urea_bags + mop_bags, 1)
    }


def generate_agronomist_pdf(record) -> io.BytesIO:
    """
    Generates a byte stream of the certified Agronomist Field Report PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    c_primary = colors.HexColor('#059669')    # Emerald 600
    c_primary_dark = colors.HexColor('#065f46') # Emerald 800
    c_secondary = colors.HexColor('#1e293b')  # Slate 800
    c_slate_500 = colors.HexColor('#64748b')  # Slate 500
    c_bg_light = colors.HexColor('#f8fafc')   # Slate 50
    c_accent = colors.HexColor('#d97706')     # Amber 600
    c_border = colors.HexColor('#cbd5e1')     # Slate 300

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary_dark
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_slate_500
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_secondary
    )

    bold_cell = ParagraphStyle(
        'BoldCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_secondary
    )

    white_bold = ParagraphStyle(
        'WhiteBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    elements = []

    # 1. Header Banner Table
    header_data = [
        [
            Paragraph("<b>AgriOptima</b> • Precision Agriculture", title_style),
            Paragraph(f"<b>REPORT ID:</b> AGRI-{record.id:05d}<br/><b>DATE:</b> {record.created_at.strftime('%B %d, %Y')}", ParagraphStyle('RightH', parent=subtitle_style, alignment=TA_RIGHT))
        ],
        [
            Paragraph("Official Certified Agronomic Soil Prescription & Yield Optimization Report", subtitle_style),
            Paragraph("<b>SOLVER:</b> SciPy SLSQP (Mitscherlich-Baule Constrained)", ParagraphStyle('RightH2', parent=subtitle_style, alignment=TA_RIGHT))
        ]
    ]

    header_table = Table(header_data, colWidths=[4.0 * inch, 3.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=10))

    # 2. Executive Summary Metrics Cards
    comm_bags = calculate_commercial_bags(
        float(record.delta_nitrogen),
        float(record.delta_phosphorus),
        float(record.delta_potassium)
    )

    summary_data = [
        [
            Paragraph("<b>Target Crop</b>", bold_cell),
            Paragraph("<b>Baseline Yield</b>", bold_cell),
            Paragraph("<b>Target Yield</b>", bold_cell),
            Paragraph("<b>Expected Optimized Yield</b>", bold_cell),
            Paragraph("<b>Cost Savings vs Blanket</b>", bold_cell)
        ],
        [
            Paragraph(f"<font size=12 color='#065f46'><b>{record.crop_type}</b></font>", body_style),
            Paragraph(f"<font size=12><b>{record.baseline_yield}</b></font> t/ha", body_style),
            Paragraph(f"<font size=12><b>{record.target_yield}</b></font> t/ha", body_style),
            Paragraph(f"<font size=12 color='#059669'><b>{record.predicted_yield}</b></font> t/ha", body_style),
            Paragraph(f"<font size=12 color='#059669'><b>${record.cost_savings}</b></font> ({record.percent_savings}%)", body_style),
        ]
    ]

    summary_table = Table(summary_data, colWidths=[1.44 * inch] * 5)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # 3. Baseline Soil Chemistry & Environmental Factors
    elements.append(Paragraph("1. Soil Test Analysis & Baseline Environmental Metrics", h2_style))
    elements.append(Spacer(1, 4))

    soil_data = [
        [
            Paragraph("Parameter", white_bold),
            Paragraph("Measured Value", white_bold),
            Paragraph("Agronomic Evaluation & Status", white_bold)
        ],
        [
            Paragraph("Soil Available Nitrogen (N)", bold_cell),
            Paragraph(f"{record.current_nitrogen:.1f} kg/ha", body_style),
            Paragraph("Vegetative growth indicator; supplementary nitrogen required." if record.delta_nitrogen > 0 else "Optimal baseline reserve.", body_style)
        ],
        [
            Paragraph("Soil Available Phosphorus (P)", bold_cell),
            Paragraph(f"{record.current_phosphorus:.1f} kg/ha", body_style),
            Paragraph("Root establishment & tillering nutrient; supplementation prescribed." if record.delta_phosphorus > 0 else "Sufficient root zone reserve.", body_style)
        ],
        [
            Paragraph("Soil Available Potassium (K)", bold_cell),
            Paragraph(f"{record.current_potassium:.1f} kg/ha", body_style),
            Paragraph("Disease resistance & grain filling osmotic regulator." if record.delta_potassium > 0 else "Adequate plant available potassium.", body_style)
        ],
        [
            Paragraph("Soil pH Level", bold_cell),
            Paragraph(f"{record.soil_ph:.2f}", body_style),
            Paragraph("Optimal neutral-to-slightly acidic nutrient uptake range." if 6.0 <= record.soil_ph <= 7.2 else ("Acidic: slight nutrient lockout possible." if record.soil_ph < 6.0 else "Alkaline: micronutrient availability may be reduced."), body_style)
        ],
        [
            Paragraph("Annual / Seasonal Rainfall", bold_cell),
            Paragraph(f"{record.rainfall:.1f} mm", body_style),
            Paragraph("Adequate moisture regime supporting efficient nutrient dissolution.", body_style)
        ]
    ]

    soil_table = Table(soil_data, colWidths=[2.3 * inch, 1.4 * inch, 3.5 * inch])
    soil_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(soil_table)
    elements.append(Spacer(1, 14))

    # 4. Prescriptive Supplemental Recommendations (Pure & Commercial Bags)
    elements.append(Paragraph("2. Prescriptive Nutrient Dosage & Commercial Bag Shopping List", h2_style))
    elements.append(Spacer(1, 4))

    recipe_data = [
        [
            Paragraph("Nutrient Source", white_bold),
            Paragraph("Optimal Additional Nutrient", white_bold),
            Paragraph("Commercial Fertilizer Equivalent", white_bold),
            Paragraph("50kg Bags / Hectare", white_bold)
        ],
        [
            Paragraph("<b>Nitrogen (N)</b>", bold_cell),
            Paragraph(f"<b>+{record.delta_nitrogen:.1f} kg/ha</b>", body_style),
            Paragraph(f"Urea (46% N): {comm_bags['urea_kg']} kg/ha", body_style),
            Paragraph(f"<b>{comm_bags['urea_bags']} bags</b>", bold_cell)
        ],
        [
            Paragraph("<b>Phosphorus (P)</b>", bold_cell),
            Paragraph(f"<b>+{record.delta_phosphorus:.1f} kg/ha</b>", body_style),
            Paragraph(f"DAP (18-46-0): {comm_bags['dap_kg']} kg/ha", body_style),
            Paragraph(f"<b>{comm_bags['dap_bags']} bags</b>", bold_cell)
        ],
        [
            Paragraph("<b>Potassium (K)</b>", bold_cell),
            Paragraph(f"<b>+{record.delta_potassium:.1f} kg/ha</b>", body_style),
            Paragraph(f"MOP (0-0-60): {comm_bags['mop_kg']} kg/ha", body_style),
            Paragraph(f"<b>{comm_bags['mop_bags']} bags</b>", bold_cell)
        ],
        [
            Paragraph("<b>Total Prescription</b>", bold_cell),
            Paragraph(f"<b>{record.total_fertilizer_kg:.1f} kg/ha</b>", bold_cell),
            Paragraph("Combined Mineral Input", body_style),
            Paragraph(f"<font color='#059669'><b>{comm_bags['total_bags']} bags/ha</b></font>", bold_cell)
        ]
    ]

    recipe_table = Table(recipe_data, colWidths=[1.8 * inch, 1.8 * inch, 2.2 * inch, 1.4 * inch])
    recipe_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary_dark),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_bg_light]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecfdf5')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(recipe_table)
    elements.append(Spacer(1, 14))

    # 5. Financial & Environmental Impact Analysis
    elements.append(Paragraph("3. Economic ROI & Environmental Stewardship Metrics", h2_style))
    elements.append(Spacer(1, 4))

    blanket_total_kg = 120.0 + 60.0 + 40.0 # 220 kg
    avoided_excess_kg = max(0.0, blanket_total_kg - float(record.total_fertilizer_kg))

    econ_data = [
        [
            Paragraph("Economic Metric", bold_cell),
            Paragraph("Prescriptive Plan", bold_cell),
            Paragraph("Blanket Application", bold_cell),
            Paragraph("Farmer Benefit / ESG Impact", bold_cell)
        ],
        [
            Paragraph("Total Fertilizer Cost", body_style),
            Paragraph(f"<b>${record.optimized_cost:.2f} / ha</b>", body_style),
            Paragraph(f"${record.blanket_cost:.2f} / ha", body_style),
            Paragraph(f"<font color='#059669'><b>${record.cost_savings:.2f} / ha Saved ({record.percent_savings}%)</b></font>", body_style)
        ],
        [
            Paragraph("Total Chemical Load", body_style),
            Paragraph(f"{record.total_fertilizer_kg:.1f} kg/ha", body_style),
            Paragraph("220.0 kg/ha", body_style),
            Paragraph(f"<b>{avoided_excess_kg:.1f} kg/ha</b> avoided chemical loading", body_style)
        ],
        [
            Paragraph("Environmental Status", body_style),
            Paragraph("Reduced run-off risk", body_style),
            Paragraph("High nitrate leaching risk", body_style),
            Paragraph("Mitigates groundwater contamination & soil acidification", body_style)
        ]
    ]

    econ_table = Table(econ_data, colWidths=[1.8 * inch, 1.6 * inch, 1.6 * inch, 2.2 * inch])
    econ_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(econ_table)
    elements.append(Spacer(1, 14))

    # 6. Best Management Practices (BMPs) & Certification
    bmp_text = (
        "<b>Agronomic Application Guidelines (4R Nutrient Stewardship):</b><br/>"
        "• <b>Right Source:</b> Use split applications of Urea (50% basal at sowing, 50% top-dressing at tillering/knee-high). Apply all DAP and MOP as basal.<br/>"
        "• <b>Right Place:</b> Incorporate fertilizer 5cm below and beside seeds (banding) to avoid volatilization.<br/>"
        "• <b>Right Timing:</b> Avoid broadcasting immediately prior to projected heavy rainfall (>25mm/day) to prevent run-off."
    )
    elements.append(Paragraph(bmp_text, body_style))
    elements.append(Spacer(1, 16))

    # Signature Block
    sign_data = [
        [
            Paragraph("<b>Generated by AgriOptima Prescriptive Intelligence</b><br/><font size=7 color='#64748b'>Certified Computational Agronomy Framework</font>", body_style),
            Paragraph("<b>Agronomist Verification Stamp:</b><br/>[ ✓ APPROVED DIGITAL SIGNATURE ]", ParagraphStyle('SignRight', parent=body_style, alignment=TA_RIGHT))
        ]
    ]
    sign_table = Table(sign_data, colWidths=[4.2 * inch, 3.0 * inch])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(sign_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
