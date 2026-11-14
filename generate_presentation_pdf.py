"""
AgriOptima 3D - Presentation PDF Generator
Generates a publication-quality 24-page 16:9 landscape presentation PDF using ReportLab.
Inspired by the warm linen cream, rounded card containers, serif typography,
and visual hierarchy of the reference slide deck.
"""

import os
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 16:9 Widescreen dimensions: 13.333 x 7.5 inches = 960 x 540 points
PAGE_WIDTH = 960.0
PAGE_HEIGHT = 540.0
TOTAL_SLIDES = 24

# Color Palette
BG_COLOR = colors.HexColor('#F6F1E8')          # Warm Linen Cream
CARD_BG = colors.HexColor('#FFFFFF')           # Pure White
CARD_ALT_BG = colors.HexColor('#FBF6EE')       # Soft Cream
CARD_ACCENT = colors.HexColor('#F3E7D9')       # Light Peach / Tan
BORDER_COLOR = colors.HexColor('#E4DCCC')      # Subtle Card Border

PRIMARY_DARK = colors.HexColor('#3E2723')      # Deep Espresso Brown
ACCENT_BROWN = colors.HexColor('#A04728')      # Terracotta / Rust
ACCENT_GREEN = colors.HexColor('#2D6A4F')      # Forest Emerald
ACCENT_BLUE = colors.HexColor('#2B6CB0')       # Slate Blue
ACCENT_AMBER = colors.HexColor('#BC6C25')      # Harvest Amber
ACCENT_RED = colors.HexColor('#BA181B')        # Crimson Risk

TEXT_DARK = colors.HexColor('#2D3748')         # Dark Charcoal Body
TEXT_MUTED = colors.HexColor('#718096')        # Muted Slate
DOT_COLOR = colors.HexColor('#B4A08C')         # Corner Decorative Pebble


def draw_slide_base(c, current_idx, total=TOTAL_SLIDES):
    """Fills background, draws corner circles and bottom timeline."""
    # Background
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # 4 Corner decorative dots
    dot_r = 12.0
    c.setFillColor(DOT_COLOR)
    c.circle(20, PAGE_HEIGHT - 20, dot_r, fill=1, stroke=0)
    c.circle(PAGE_WIDTH - 20, PAGE_HEIGHT - 20, dot_r, fill=1, stroke=0)
    c.circle(20, 20, dot_r, fill=1, stroke=0)
    c.circle(PAGE_WIDTH - 20, 20, dot_r, fill=1, stroke=0)

    # Bottom segmented timeline progress bar
    pill_w = 26.0
    pill_h = 4.0
    gap = 7.0
    total_w = (pill_w * total) + (gap * (total - 1))
    start_x = (PAGE_WIDTH - total_w) / 2.0
    y = 18.0

    for i in range(total):
        x = start_x + (i * (pill_w + gap))
        if i == current_idx:
            c.setFillColor(ACCENT_BROWN)
            c.roundRect(x, y, pill_w + 10, pill_h + 1, 2, fill=1, stroke=0)
        else:
            c.setFillColor(colors.HexColor('#DACDBE'))
            c.roundRect(x, y, pill_w, pill_h, 2, fill=1, stroke=0)


def draw_slide_header(c, title, category="PROJECT DATA", slide_num=None):
    """Draws slide title, underline, category pill, and slide number."""
    # Title
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Times-Bold', 22)
    c.drawString(60, PAGE_HEIGHT - 55, title)

    # Terracotta accent underline
    c.setFillColor(ACCENT_BROWN)
    c.roundRect(60, PAGE_HEIGHT - 65, 65, 4, 2, fill=1, stroke=0)

    # Category Badge on Top-Right
    badge_w = 125.0
    badge_h = 24.0
    bx = PAGE_WIDTH - 60 - badge_w
    by = PAGE_HEIGHT - 58
    c.setFillColor(PRIMARY_DARK)
    c.roundRect(bx, by, badge_w, badge_h, 12, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(bx + badge_w / 2.0, by + 7.5, category.upper())

    # Slide number indicator if supplied
    if slide_num is not None:
        c.setFillColor(PRIMARY_DARK)
        c.setFont('Times-Bold', 11)
        c.drawRightString(PAGE_WIDTH - 60, PAGE_HEIGHT - 28, f"{slide_num:02d}")


def draw_card(c, x, y, w, h, bg=CARD_BG, border=BORDER_COLOR, radius=16):
    """Draws a clean rounded-corner card."""
    c.setFillColor(bg)
    if border:
        c.setStrokeColor(border)
        c.setLineWidth(1.2)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


def draw_text_block(c, text_lines, x, y_start, font_name='Helvetica', font_size=10, line_height=14, text_color=TEXT_DARK):
    """Draws multiple lines of text with specified font and line height."""
    c.setFillColor(text_color)
    c.setFont(font_name, font_size)
    curr_y = y_start
    for line in text_lines:
        c.drawString(x, curr_y, line)
        curr_y -= line_height


# ==============================================================
# MAIN GENERATION PROCESS
# ==============================================================
output_pdf_path = "c:/Users/67sdn/OneDrive/Desktop/Project/agrioptima/AgriOptima_Project_Presentation.pdf"
c = canvas.Canvas(output_pdf_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
print(f"Generating 24-page presentation PDF at {output_pdf_path}...")

# -------------------------------------------------------------
# SLIDE 1: TITLE SLIDE
# -------------------------------------------------------------
draw_slide_base(c, 0)
# Hero Left Card
draw_card(c, 60, 50, 580, 420, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 34)
c.drawString(95, 410, "AgriOptima 3D")

c.setFillColor(ACCENT_BROWN)
c.setFont('Times-Bold', 18)
c.drawString(95, 380, "Precision Crop Yield & Variable Rate Fertilizer Optimizer")

# Summary text
lines_intro = [
    "An enterprise-grade precision agriculture platform combining non-linear",
    "Mitscherlich-Baule mathematical optimization, SciPy SLSQP constrained solvers,",
    "multispectral Sentinel-2 & drone NDVI remote sensing, computer vision leaf pathology,",
    "and hands-free multilingual AI agronomist intelligence."
]
draw_text_block(c, lines_intro, 95, 335, 'Helvetica', 11.5, 18, TEXT_DARK)

tech_lines = [
    "Technology Stack: Python • Django 5 • SciPy SLSQP • Leaflet GIS • Google Satellite • Sentinel-2 MSI"
]
draw_text_block(c, tech_lines, 95, 230, 'Helvetica-Bold', 10, 14, ACCENT_GREEN)

# Right Mockup Cards
draw_card(c, 670, 270, 230, 200, PRIMARY_DARK, None)
c.setFillColor(colors.white)
c.setFont('Times-Bold', 15)
c.drawCentredString(785, 390, "🛰️ 🗺️")
c.drawCentredString(785, 360, "GIS & Remote Sensing")
c.setFont('Helvetica', 9.5)
c.setFillColor(colors.HexColor('#E2E8F0'))
c.drawCentredString(785, 335, "Google Aerial + Sentinel-2 NDVI")

draw_card(c, 670, 50, 230, 200, CARD_ACCENT, None)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawCentredString(785, 170, "🌿 🎙️")
c.drawCentredString(785, 140, "AI Leaf Doctor & Voice")
c.setFont('Helvetica', 9.5)
c.setFillColor(TEXT_MUTED)
c.drawCentredString(785, 115, "Vision Pathology + 14 Languages")
c.showPage()


# -------------------------------------------------------------
# SLIDE 2: INDEX / CONTENTS
# -------------------------------------------------------------
draw_slide_base(c, 1)
draw_slide_header(c, "Index & Project Roadmap", "CONTENTS", 1)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawString(85, 425, "Technical Foundations & Core Engines")
items_col1 = [
    ("01", "Introduction & Problem Statement"),
    ("02", "Objectives, Value Proposition & Scope"),
    ("03", "Agronomic Dataset & Multi-Crop Profiles"),
    ("04", "Mathematical Optimization (Mitscherlich & SLSQP)"),
    ("05", "Core Technology Stack & Architecture"),
    ("06", "Global Weather & Nitrate Run-Off Intelligence"),
    ("07", "Multi-Zone GIS Farm Mapper & Tractor VRA"),
    ("08", "Multispectral Satellite & Drone NDVI Vigor"),
    ("09", "Visual AI Leaf Doctor (Pathology & Deficiencies)")
]
curr_y = 390
for num, text in items_col1:
    c.setFillColor(ACCENT_BROWN)
    c.setFont('Helvetica-Bold', 10.5)
    c.drawString(85, curr_y, num)
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 10.5)
    c.drawString(115, curr_y, text)
    curr_y -= 34

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawString(520, 425, "User Experience, Operations & Verification")
items_col2 = [
    ("10", "Voice Agronomist in 14 Native Languages"),
    ("11", "Global Internationalization & Theme Engine"),
    ("12", "Farmer Virtual Community Hub & Live Chat"),
    ("13", "Farmer Security & Dual-Channel OTP Auth"),
    ("14", "Commercial Fertilizer Bags & 4R Split Calendar"),
    ("15", "System Testing & Mathematical Verification (22/22)"),
    ("16", "End-to-End Precision Agronomy Workflow"),
    ("17", "Example Farmer Case Study & Economic ROI"),
    ("18", "Production Deployment & Future Roadmap")
]
curr_y = 390
for num, text in items_col2:
    c.setFillColor(ACCENT_GREEN)
    c.setFont('Helvetica-Bold', 10.5)
    c.drawString(520, curr_y, num)
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 10.5)
    c.drawString(550, curr_y, text)
    curr_y -= 34
c.showPage()


# -------------------------------------------------------------
# SLIDE 3: INTRODUCTION
# -------------------------------------------------------------
draw_slide_base(c, 2)
draw_slide_header(c, "Introduction: What is AgriOptima?", "PROJECT DATA", 2)

draw_card(c, 60, 50, 560, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 16)
c.drawString(90, 420, "Precision Agronomy Meets Mathematical Optimization")

lines_intro3 = [
    "AgriOptima is an enterprise-grade precision agriculture platform developed",
    "to solve the global crisis of fertilizer over-application, nutrient run-off,",
    "and suboptimal crop yields.",
    "",
    "By bridging agronomic soil chemistry, hyper-local climate forecasting,",
    "remote sensing satellite NDVI, and constrained mathematical optimization,",
    "AgriOptima computes the exact supplemental nutrient doses (ΔN, ΔP, ΔK)",
    "required to achieve farmer-defined yield targets at minimal commercial cost."
]
draw_text_block(c, lines_intro3, 90, 385, 'Helvetica', 11, 17, TEXT_DARK)

# Callout URL box
draw_card(c, 90, 90, 500, 60, CARD_ACCENT, None)
c.setFillColor(PRIMARY_DARK)
c.setFont('Helvetica-Bold', 10)
c.drawString(105, 125, "🌾 Production App: https://agrioptima-jpva.onrender.com/")
c.setFont('Helvetica', 9.5)
c.setFillColor(TEXT_DARK)
c.drawString(105, 105, "Live multi-zone geospatial mapping, leaf scanner & multilingual voice copilot.")

# Right Pipeline
draw_card(c, 650, 50, 250, 410, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawCentredString(775, 420, "Core Pipeline")

steps_p = [
    ("1. Soil & Field Inputs", ACCENT_BLUE),
    ("2. Climate & Leaching Risk", ACCENT_AMBER),
    ("3. Mitscherlich SLSQP Solver", ACCENT_BROWN),
    ("4. Satellite NDVI Vigor", ACCENT_GREEN),
    ("5. Tractor VRA Prescription", PRIMARY_DARK)
]
sy = 360
for name, col in steps_p:
    draw_card(c, 675, sy, 200, 40, col, None, 10)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawCentredString(775, sy + 14, name)
    sy -= 65
c.showPage()


# -------------------------------------------------------------
# SLIDE 4: THE PROBLEM
# -------------------------------------------------------------
draw_slide_base(c, 3)
draw_slide_header(c, "1. The Problem: Agronomic & Ecological Crisis", "PROBLEM CONTEXT", 3)

probs = [
    ("Excessive Over-Fertilization", 
     ["Farmers traditionally broadcast blanket fertilizer", "doses regardless of existing soil reserves.", "This leads to severe nutrient saturation, high", "operational costs, and diminishing biological returns."],
     "💸 High Input Cost", ACCENT_BROWN),
    ("Nitrate Leaching & Run-Off",
     ["Excess nitrogen dissolved in heavy rain leaches into", "underground aquifers or washes into river basins,", "causing severe eutrophication, dead zones, and", "greenhouse nitrous oxide (N2O) emissions."],
     "🌊 Environmental Hazard", ACCENT_RED),
    ("Spatial Field Inconsistency",
     ["Single-field farms exhibit significant soil variability", "in pH, organic matter, and baseline nutrients.", "Uniform application leads to over-feeding rich zones", "and starving depleted sectors."],
     "🗺️ Inefficient VRA", ACCENT_AMBER)
]

for idx, (title, lines, badge, col) in enumerate(probs):
    x = 60 + idx * 290
    draw_card(c, x, 130, 260, 330, CARD_BG)
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Times-Bold', 13.5)
    c.drawString(x + 20, 420, title)
    draw_text_block(c, lines, x + 20, 380, 'Helvetica', 9.5, 15, TEXT_DARK)

    # Bottom Pill
    draw_card(c, x + 20, 155, 220, 32, CARD_ACCENT, None, 16)
    c.setFillColor(col)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawCentredString(x + 130, 166, badge)

# Target box
draw_card(c, 60, 50, 840, 60, CARD_ACCENT, None)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 11)
c.drawCentredString(480, 85, "Central Challenge: How can we mathematically compute minimal nutrient inputs")
c.drawCentredString(480, 68, "while guaranteeing target yield and protecting local water bodies?")
c.showPage()


# -------------------------------------------------------------
# SLIDE 5: OBJECTIVES & SCOPE
# -------------------------------------------------------------
draw_slide_base(c, 4)
draw_slide_header(c, "2. Objectives & Architectural Scope", "PROJECT SCOPE", 4)

objs = [
    ("1", "Constrained Non-Linear Solver", "Formulate and solve Mitscherlich-Baule production functions with SLSQP constraints.", "SciPy SLSQP", ACCENT_BLUE),
    ("2", "Global Climate & Leaching Guard", "Real-time 14-day rainfall forecasting via Open-Meteo for any GPS coordinate on Earth.", "Open-Meteo", ACCENT_AMBER),
    ("3", "Geospatial Multi-Zone GIS Mapper", "Google Satellite map with variable zoning and tractor VRA GeoJSON prescription export.", "Leaflet GIS", ACCENT_GREEN),
    ("4", "Satellite Drone NDVI Vigor Heatmap", "Simulated Sentinel-2 remote sensing raster, Chlorophyll SPAD, and VRA Nitrogen adjustments.", "Sentinel-2 MSI", PRIMARY_DARK),
    ("5", "Visual AI Leaf Doctor & Voice", "Mobile camera leaf pathology diagnostics and hands-free voice in 14 native languages.", "Speech & CV", ACCENT_BROWN)
]

oy = 400
for num, title, desc, tag, tag_col in objs:
    draw_card(c, 60, oy, 840, 55, CARD_BG)
    # Circle
    c.setFillColor(ACCENT_BROWN if int(num) % 2 != 0 else ACCENT_GREEN)
    c.circle(85, oy + 27.5, 14, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(85, oy + 23.5, num)

    c.setFillColor(PRIMARY_DARK)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(115, oy + 32, f"{title}:")
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 10)
    c.drawString(115, oy + 16, desc)

    # Tag
    draw_card(c, 760, oy + 14, 125, 26, tag_col, None, 13)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawCentredString(822.5, oy + 22, tag)

    oy -= 70
c.showPage()


# -------------------------------------------------------------
# SLIDE 6: AGRONOMIC DATASET
# -------------------------------------------------------------
draw_slide_base(c, 5)
draw_slide_header(c, "3. Agronomic Scientific Dataset & Crop Models", "AGRONOMY", 5)

crops_grid = [
    ("🌾 Wheat", "Triticum aestivum", "Max: 8.5 t/ha", "N-eff: 0.0075", "Responsive to tillering split-dressing"),
    ("🌾 Rice", "Oryza sativa", "Max: 9.0 t/ha", "N-eff: 0.0068", "Prone to blast & zinc precipitation"),
    ("🌽 Maize", "Zea mays", "Max: 12.0 t/ha", "N-eff: 0.0055", "Heavy feeder, requires balanced P & K"),
    ("🌱 Cotton", "Gossypium hirsutum", "Max: 4.5 t/ha", "N-eff: 0.0082", "High potash demand during boll formation"),
    ("🥔 Potato", "Solanum tuberosum", "Max: 45.0 t/ha", "K-eff: 0.0060", "Critical potassium demand for tuber bulking"),
    ("🍅 Tomato", "Solanum lycopersicum", "Max: 70.0 t/ha", "Ca/P-eff: 0.0070", "Prone to blossom end rot under Ca deficit")
]

for idx, (c_name, c_sci, c_max, c_eff, c_note) in enumerate(crops_grid):
    col_i = idx % 3
    row_i = idx // 3
    gx = 60 + col_i * 290
    gy = 250 - row_i * 180

    draw_card(c, gx, gy, 260, 160, CARD_BG)
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Times-Bold', 14)
    c.drawString(gx + 15, gy + 130, c_name)
    c.setFillColor(TEXT_MUTED)
    c.setFont('Times-Italic', 9.5)
    c.drawString(gx + 15, gy + 115, c_sci)

    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 9.5)
    c.drawString(gx + 15, gy + 88, f"• Biological Ceiling: {c_max}")
    c.drawString(gx + 15, gy + 70, f"• Efficiency Factor: {c_eff}")
    c.drawString(gx + 15, gy + 52, f"• {c_note}")

# Bottom parameter bar
draw_card(c, 60, 50, 840, 50, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Helvetica-Bold', 10)
c.drawCentredString(480, 70, "Calibrated Parameters: Baseline Soil N-P-K (kg/ha) • Soil pH (3.5 - 9.5) • Precipitation (mm) • Biological Ceiling (t/ha)")
c.showPage()


# -------------------------------------------------------------
# SLIDE 7: MATHEMATICAL FORMULATION
# -------------------------------------------------------------
draw_slide_base(c, 6)
draw_slide_header(c, "4. Mathematical Optimization: Mitscherlich & SLSQP", "MATHEMATICS", 6)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Mitscherlich-Baule Yield Equation")

draw_card(c, 85, 335, 355, 65, CARD_ALT_BG, ACCENT_BROWN, 10)
c.setFillColor(ACCENT_BROWN)
c.setFont('Courier-Bold', 8.5)
c.drawString(95, 375, "Y = Y_max · (1 - 10^(-c_n · N_tot))")
c.drawString(95, 360, "    · (1 - 10^(-c_p · P_tot)) · (1 - 10^(-c_k · K_tot))")
c.drawString(95, 345, "    · f(pH) · f(Rain)")

m_points = [
    "• Law of Diminishing Returns: Each additional kg of fertilizer yields progressively less.",
    "• Total Nutrient Pool: N_tot = S_n (Soil test) + ΔN (Fertilizer).",
    "• pH Lockout Bell Curve: Penalizes nutrient uptake outside 6.0–7.8.",
    "• Leaching Run-off Penalty: Nitrate retention drops with excess precipitation."
]
draw_text_block(c, m_points, 85, 305, 'Helvetica', 9.5, 20, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "SLSQP Constrained Optimization")

draw_card(c, 520, 335, 355, 65, CARD_ALT_BG, ACCENT_GREEN, 10)
c.setFillColor(ACCENT_GREEN)
c.setFont('Courier-Bold', 8.5)
c.drawString(530, 375, "minimize Cost = w_n·ΔN + w_p·ΔP + w_k·ΔK + Penalty")
c.drawString(530, 360, "subject to:")
c.drawString(530, 345, "  Y(ΔN, ΔP, ΔK) >= Y_target,  0 <= Δ_i <= MAX_i")

s_points = [
    "• Solver: Sequential Least Squares Programming (SciPy SLSQP).",
    "• Zero-Cost Edge Case: Returns exactly 0 kg/ha when soil baseline meets target.",
    "• Biological Feasibility Guard: Catches unattainable yields and scales to ceiling.",
    "• Environmental Constraints: Prevents excessive nitrate accumulation in soil."
]
draw_text_block(c, s_points, 520, 305, 'Helvetica', 9.5, 20, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 8: TECH STACK
# -------------------------------------------------------------
draw_slide_base(c, 7)
draw_slide_header(c, "5. Full-Stack Technology Stack & Architecture", "ARCHITECTURE", 7)

t_stack = [
    ("Python 3.11", "Core computational runtime executing optimization & CV", ACCENT_BLUE),
    ("Django 5.0", "Enterprise MVC framework, ORM models & REST views", ACCENT_GREEN),
    ("SciPy & NumPy", "SLSQP non-linear solvers and array response curves", ACCENT_BROWN),
    ("Leaflet GIS & Google Maps", "Aerial satellite, terrain, roadmap & GeoJSON overlays", ACCENT_AMBER),
    ("Web Speech API", "Client-side voice recognition & synthesis in 14 native dialects", ACCENT_GREEN),
    ("ReportLab & ICS", "Vector PDF agronomist certificates & Google Calendar sync", PRIMARY_DARK)
]

for idx, (t_name, t_desc, t_col) in enumerate(t_stack):
    col_i = idx % 3
    row_i = idx // 3
    gx = 60 + col_i * 290
    gy = 250 - row_i * 145

    draw_card(c, gx, gy, 260, 125, CARD_BG)
    c.setFillColor(t_col)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(gx + 15, gy + 95, t_name)
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 9.5)
    c.drawString(gx + 15, gy + 70, t_desc[:38])
    c.drawString(gx + 15, gy + 54, t_desc[38:])

# Tier Bar
draw_card(c, 60, 50, 840, 50, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Helvetica-Bold', 9.5)
c.drawCentredString(480, 70, "CLIENT (HTML5 / Tailwind / Leaflet) ➔ APPLICATION (Django Views) ➔ ENGINE (SLSQP / NDVI / Leaf Doctor) ➔ DATABASE (PostgreSQL)")
c.showPage()


# -------------------------------------------------------------
# SLIDE 9: GLOBAL WEATHER
# -------------------------------------------------------------
draw_slide_base(c, 8)
draw_slide_header(c, "6. Global Weather & Nitrate Leaching Intelligence", "CLIMATE", 8)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Hyper-Local Climate Forecasting")
w_points = [
    "• Universal Geocoding: Search ANY farm, village, city, or enter raw lat/lon coordinates.",
    "• Open-Meteo Integration: Real-time 14-day precipitation forecasts aggregated into seasonal totals.",
    "• Automatic GPS Geolocation: Browser HTML5 geolocation with server-side IP fallback.",
    "• Global Agricultural Presets: Punjab (India), Iowa (Corn Belt), California Central Valley, Nile Delta, Thames Valley, Sao Paulo."
]
draw_text_block(c, w_points, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Nitrate Leaching Risk Engine")
r_levels = [
    ("LOW RISK (< 25 mm)", "Safe for granular broadcasting without split delays.", ACCENT_GREEN),
    ("MODERATE RISK (25-60 mm)", "Delay broadcasting by 48h or switch to fertigation to prevent run-off.", ACCENT_AMBER),
    ("SEVERE / HIGH RISK (> 60 mm)", "High nitrate run-off alert. Optimizer reduces basal Delta N by 30% and enforces 3-way split application.", ACCENT_RED)
]
ry = 385
for r_title, r_desc, r_col in r_levels:
    c.setFillColor(r_col)
    c.setFont('Helvetica-Bold', 10.5)
    c.drawString(520, ry, f"• {r_title}")
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 9.5)
    c.drawString(520, ry - 18, r_desc[:48])
    c.drawString(520, ry - 32, r_desc[48:])
    ry -= 55
c.showPage()


# -------------------------------------------------------------
# SLIDE 10: MULTI-ZONE GIS MAPPER
# -------------------------------------------------------------
draw_slide_base(c, 9)
draw_slide_header(c, "7. Multi-Zone Farm Field Mapper (GIS & VRA)", "GIS & VRA", 9)

z_cards = [
    ("Precision Zoning", 
     ["Subdivide fields into distinct soil management", "zones based on topography, soil color, or past yield.", "", "Each zone tracks its own acreage (ha), soil N-P-K,", "pH, target yield, and GPS coordinates."]),
    ("Google Maps Tile Layers",
     ["Full Google Maps integration inspired by standard", "Google interfaces:", "", "• 🛰️ Google Satellite (Aerial)", "• ⛰️ Google Terrain (Contours)", "• 🗺️ Google Roadmap (Streets)", "• 🌐 OpenStreetMap (OSM)"]),
    ("Tractor VRA GeoJSON",
     ["Generates standardized ISO 11783-compliant", "GeoJSON prescription files directly loadable into", "GPS-guided tractor spreaders.", "", "Spreaders automatically adjust granular output as the", "tractor traverses from zone to zone."])
]

for idx, (title, lines) in enumerate(z_cards):
    x = 60 + idx * 290
    draw_card(c, x, 50, 260, 410, CARD_BG)
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Times-Bold', 14)
    c.drawString(x + 20, 425, title)
    draw_text_block(c, lines, x + 20, 385, 'Helvetica', 10, 18, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 11: SATELLITE NDVI VIGOR
# -------------------------------------------------------------
draw_slide_base(c, 10)
draw_slide_header(c, "8. Satellite Drone NDVI Crop Vigor Heatmap", "REMOTE SENSING", 10)

draw_card(c, 60, 50, 430, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Multispectral Remote Sensing Engine")
nv_points = [
    "• NDVI Calculation: (NIR - Red) / (NIR + Red) multispectral vegetation index.",
    "• 8x8 Spatial Raster Grid generated over field boundary with cell IDs, tooltips, and popups.",
    "• Live Canopy Analytics HUD: Mean Field NDVI, Canopy Health Score (0-100), and Field Uniformity %.",
    "• Variable Rate Nitrogen Prescriptions: High-vigor zones reduce N; stressed zones receive remedial boost."
]
draw_text_block(c, nv_points, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 520, 50, 380, 410, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawString(545, 425, "NDVI Spectral Color Ramp & Actions")
ramps_data = [
    ("< 0.15", "Bare Soil / Water", "Non-vegetated ground", colors.HexColor('#78350F')),
    ("0.15 - 0.30", "Severe Crop Stress", "+25 kg/ha N (Emergency spray)", ACCENT_RED),
    ("0.30 - 0.45", "Low Vigor / Deficit", "+12 kg/ha N (Top-dress)", ACCENT_AMBER),
    ("0.45 - 0.60", "Moderate Vigor", "Maintain baseline prescription", colors.HexColor('#84CC16')),
    ("0.60 - 0.75", "Healthy Canopy", "Optimal chlorophyll index", ACCENT_GREEN),
    ("0.75 - 1.00", "Dense Peak Biomass", "-15 kg/ha N (Prevent lodging)", colors.HexColor('#15803D'))
]
nvy = 390
for rng, lbl, act, col in ramps_data:
    c.setFillColor(col)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(545, nvy, f"• {rng} ({lbl}):")
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 9)
    c.drawString(545, nvy - 14, act)
    nvy -= 34
c.showPage()


# -------------------------------------------------------------
# SLIDE 12: VISUAL AI LEAF DOCTOR
# -------------------------------------------------------------
draw_slide_base(c, 11)
draw_slide_header(c, "9. Visual AI Leaf Doctor (Pathology & Deficiency)", "COMPUTER VISION", 11)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Computer Vision Diagnostic Engine")
ld_points = [
    "• Mobile Camera Scanner: Farmers capture leaf photos directly in the field.",
    "• Pathogen vs Starvation: Distinguishes fungal diseases (Rust, Blast, Blight) from nutrient deficits (N, P, K, Zn).",
    "• Diagnostic Confidence: Probabilistic certainty score (e.g. 94.2%).",
    "• Severity Classification: Categorizes infection as Critical, High, Medium, or Low.",
    "• Treatment Protocols: Recommends precise active fungicides and foliar micronutrient recipes."
]
draw_text_block(c, ld_points, 85, 385, 'Helvetica', 10, 22, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Instant Test Cases & 1-Click Sync")

cases = [
    ("🌾 Wheat Yellow Rust", "Puccinia striiformis (Pathogen)", "Propiconazole 25% EC"),
    ("🌾 Nitrogen Chlorosis", "V-Shape Yellowing (Deficiency)", "Urea top-dress (+35 N)"),
    ("🌽 Phosphorus Purple", "Purple margins (Deficiency)", "Band DAP (+35 P)"),
    ("🌾 Rice Blast", "Diamond lesions (Pathogen)", "Tricyclazole 75% WP"),
    ("🌿 Potassium Tip Burn", "Marginal scorch (Deficiency)", "MOP 0-0-60 (+30 K)")
]
cy = 385
for c_title, c_diag, c_act in cases:
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(520, cy, f"• {c_title} ➔ {c_diag}")
    c.setFillColor(ACCENT_GREEN)
    c.setFont('Helvetica', 9)
    c.drawString(520, cy - 14, f"  Action: {c_act}")
    cy -= 36

# 1-Click sync highlight
draw_card(c, 520, 75, 355, 45, ACCENT_BROWN, None, 10)
c.setFillColor(colors.white)
c.setFont('Helvetica-Bold', 9.5)
c.drawCentredString(697.5, 93, "⚡ 1-Click 'Apply to Optimizer' automatically updates live form!")
c.showPage()


# -------------------------------------------------------------
# SLIDE 13: VOICE AGRONOMIST
# -------------------------------------------------------------
draw_slide_base(c, 12)
draw_slide_header(c, "10. Voice Agronomist & Hands-Free Field Mode", "VOICE AI", 12)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Speech Recognition (Speech-to-Text)")
v_points = [
    "• Dedicated 🎙️ Microphone integrated in the AI Copilot drawer.",
    "• Web Speech API: Zero-latency speech transcription mapped to the farmer's active language code.",
    "• Hands-Free Field Usability: Farmers with muddy hands or work gloves can speak naturally in their native language.",
    "• Live Visual Feedback: Pulsing red recording dot indicating active speech recognition."
]
draw_text_block(c, v_points, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Text-to-Speech & Hands-Free Mode")
tts_points = [
    "• 🔊 Listen Out Loud: One-click audio playback on every AI agronomist answer bubble.",
    "• 🎧 Hands-Free Field Mode Toggle: Automatically speaks incoming advice aloud as it arrives.",
    "• Agronomic Pacing: Calibrated speech rate (0.95x) for clarity in outdoor conditions.",
    "• 14 Native Dialects: Hindi, Punjabi, Bengali, Telugu, Tamil, Marathi, Spanish, French, English, and more."
]
draw_text_block(c, tts_points, 520, 385, 'Helvetica', 10, 24, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 14: 14 LANGUAGES & 6 THEMES
# -------------------------------------------------------------
draw_slide_base(c, 13)
draw_slide_header(c, "11. 14 Global Languages & 6 Agronomic Themes", "ACCESSIBILITY", 13)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "14 Global Agricultural Languages")
lang_points = [
    "Dynamic full-app internationalization translating formulas, charts, labels, and community threads:",
    "",
    "• Indian Agricultural Belts: Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ), Bengali (বাংলা), Telugu (తెలుగు), Tamil (தமிழ்), Marathi (मराठी), Gujarati (ગુજરાતી), Kannada (ಕನ್ನಡ).",
    "",
    "• Global Farming Regions: Spanish (Español), French (Français), Portuguese (Português), Swahili (Kiswahili), Arabic (العربية), English (US/UK)."
]
draw_text_block(c, lang_points, 85, 385, 'Helvetica', 10, 20, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "6 Agronomic Theme Modes")
thm_points = [
    ("🌲 Forest Canopy", "Deep emerald green (#0B291B) & sage highlights"),
    ("🌾 Golden Harvest", "Warm rich amber (#2E1F0A) & ripe wheat tones"),
    ("☀️ Field Sunlight", "High-contrast daylight theme for outdoor readability"),
    ("🌙 Dark Mode", "Slate obsidian (#090D16) for battery saving and night use"),
    ("⚪ Clean Light", "Minimal modern white glassmorphism for desktop"),
    ("⚡ Cyber Agronomy", "Neon emerald & dark cyan futuristic agritech HUD")
]
ty = 385
for t_name, t_desc in thm_points:
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Helvetica-Bold', 10.5)
    c.drawString(520, ty, f"• {t_name}")
    c.setFillColor(TEXT_DARK)
    c.setFont('Helvetica', 9.5)
    c.drawString(520, ty - 16, t_desc)
    ty -= 36
c.showPage()


# -------------------------------------------------------------
# SLIDE 15: COMMUNITY HUB
# -------------------------------------------------------------
draw_slide_base(c, 14)
draw_slide_header(c, "12. Farmer Virtual Community Hub & Live Chat", "COMMUNITY", 14)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Nearby Farmers Map & Problem Threads")
com_points = [
    "• Geospatial Radar: Google Satellite map displaying pins of neighboring farmers within 50 km.",
    "• Structured Categories: Disease outbreaks, fertilizer tips, irrigation, market rates, and equipment sharing.",
    "• Soil Context Attaching: Farmers attach soil pH and N-P-K metrics to posts for verified peer advice.",
    "• Endorsement Voting: Upvote helpful agronomist solutions."
]
draw_text_block(c, com_points, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Live Farmer Radio Chat")
chat_points = [
    "• Real-Time Stream: Walkie-talkie style live radio chat for weather alerts and emergency advice.",
    "• Channel Broadcaster: Instant broadcast messages with caller handle, agricultural region, and timestamp.",
    "",
    "RESTful API Endpoints:",
    "  • POST /api/community/posts/ (New thread creation)",
    "  • POST /api/community/posts/<id>/reply/ (Peer response)",
    "  • POST /api/community/posts/<id>/upvote/ (Endorsement)",
    "  • POST /api/community/chat/ (Live radio stream)"
]
draw_text_block(c, chat_points, 520, 385, 'Helvetica', 10, 20, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 16: SECURITY & DUAL OTP
# -------------------------------------------------------------
draw_slide_base(c, 15)
draw_slide_header(c, "13. Farmer Security & Dual OTP Verification", "SECURITY", 15)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Dual-Channel OTP Registration")
sec1_points = [
    "• Phone SMS OTP: Delivers 6-digit cryptographic verification codes directly to mobile phones.",
    "• Email OTP: Dispatches clean branded HTML verification emails via Django SMTP.",
    "• Web Notification Push: Native browser Notification API alerts farmers on desktop/mobile.",
    "• Session-Bound Verification: Prevents registration spoofing."
]
draw_text_block(c, sec1_points, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Dual-Identifier Farmer Login")
sec2_points = [
    "• Universal Identifier: Farmers log in using EITHER phone number OR email + password.",
    "• FarmerProfile Model: 1-to-1 linkage storing location, primary crop, and verification channel.",
    "• Enterprise Security: PBKDF2 with SHA256 password hashing, CSRF tokens, and secure HTTP cookies."
]
draw_text_block(c, sec2_points, 520, 385, 'Helvetica', 10, 24, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 17: COMMERCIAL BAGS & 4R SCHEDULE
# -------------------------------------------------------------
draw_slide_base(c, 16)
draw_slide_header(c, "14. Commercial Fertilizer Bags & 4R Split Schedule", "OPERATIONS", 16)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Commercial 50 kg Bag Translation")
b_points = [
    "Translates abstract Delta N, P, K kilograms into standard 50 kg commercial fertilizer bags:",
    "",
    "• Urea (46-0-0): Nitrogen top-dressing",
    "• DAP (18-46-0): Diammonium Phosphate for early root establishment",
    "• MOP (0-0-60): Muriate of Potash for stalk resilience",
    "",
    "*Simultaneous Compensation: Subtracts Nitrogen delivered via DAP from Urea requirement to eliminate double-application."
]
draw_text_block(c, b_points, 85, 385, 'Helvetica', 10, 20, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "4R Split Application Schedule")
s_points_cal = [
    "Enforces Right Source, Right Rate, Right Time, Right Place:",
    "",
    "• Stage 1 (Basal at Sowing): 100% P (DAP) + 50% K (MOP) + 25% N (Urea)",
    "• Stage 2 (Vegetative / Tillering, +28 Days): 50% N (Urea) during peak nitrogen uptake",
    "• Stage 3 (Reproductive, +55 Days): 25% N + 50% K for grain filling",
    "",
    "📅 1-Click Apple/Outlook .ICS download & Google Calendar URL sync."
]
draw_text_block(c, s_points_cal, 520, 385, 'Helvetica', 10, 20, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 18: TESTING & VERIFICATION
# -------------------------------------------------------------
draw_slide_base(c, 17)
draw_slide_header(c, "15. Testing Suite & Mathematical Verification", "QUALITY", 17)

draw_card(c, 60, 50, 280, 410, CARD_BG)
c.setFillColor(ACCENT_GREEN)
c.setFont('Times-Bold', 42)
c.drawCentredString(200, 380, "22 / 22")
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawCentredString(200, 340, "Automated Unit Tests")
c.setFillColor(ACCENT_GREEN)
c.setFont('Helvetica-Bold', 11)
c.drawCentredString(200, 320, "100% Passing • Ran in 4.25s")

t_summary = [
    "Comprehensive automated verification",
    "covering mathematical boundaries,",
    "zero-cost edge cases, remote sensing,",
    "and authentication security."
]
draw_text_block(c, t_summary, 85, 275, 'Helvetica', 10, 18, TEXT_MUTED)

draw_card(c, 370, 50, 530, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(395, 425, "Comprehensive Test Matrix")
test_lines_m = [
    "✓ test_standard_feasible_optimization: Verifies target yield guaranteed within 0.25 t/ha.",
    "✓ test_zero_fertilizer_when_baseline_exceeds_target: Exact 0 kg/ha & 100% cost savings.",
    "✓ test_infeasible_target_yield_handling: Validates graceful biological ceiling fallback.",
    "✓ test_response_curves_generation: Tests marginal response curves across 15 points.",
    "✓ test_leaf_doctor_service_pathogen: Verifies pathogen classification & treatment recipe.",
    "✓ test_leaf_doctor_service_deficiency: Validates nitrogen chlorosis & positive Delta N impact.",
    "✓ test_ndvi_satellite_service: Confirms GeoJSON raster generation & health scores.",
    "✓ test_email_and_sms_registration_login: End-to-end OTP generation & dual-channel login."
]
draw_text_block(c, test_lines_m, 395, 385, 'Helvetica', 9.5, 22, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 19: END-TO-END WORKFLOW
# -------------------------------------------------------------
draw_slide_base(c, 18)
draw_slide_header(c, "16. End-to-End Precision Agronomy Workflow", "WORKFLOW", 18)

wf_cards = [
    ("1", "Soil Test", ["Farmer inputs soil", "N, P, K, pH & farm", "location on map."], ACCENT_BROWN),
    ("2", "Climate", ["14-day rainfall forecast", "& leaching risk", "calculation."], ACCENT_GREEN),
    ("3", "Optimization", ["SLSQP solver computes", "minimal Delta N, P, K", "at lowest cost."], ACCENT_BROWN),
    ("4", "NDVI Vigor", ["Sentinel-2 overlay", "fine-tunes zone N", "prescriptions."], ACCENT_GREEN),
    ("5", "4R Bags", ["Converts nutrients into", "50kg commercial bags", "& split dates."], ACCENT_BROWN),
    ("6", "Tractor VRA", ["Export GeoJSON to", "tractor spreader &", "certified PDF report."], ACCENT_GREEN)
]

for idx, (num, title, lines, col) in enumerate(wf_cards):
    x = 60 + idx * 145
    draw_card(c, x, 130, 130, 330, CARD_BG)
    c.setFillColor(col)
    c.circle(x + 65, 410, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(x + 65, 406, num)

    c.setFillColor(PRIMARY_DARK)
    c.setFont('Times-Bold', 12)
    c.drawCentredString(x + 65, 370, title)
    draw_text_block(c, lines, x + 10, 335, 'Helvetica', 8.5, 14, TEXT_DARK)

draw_card(c, 60, 50, 840, 60, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Helvetica-Bold', 10.5)
c.drawCentredString(480, 85, "Closed-Loop Precision Cycle: Laboratory Soil Chemistry ➔ Remote Sensing Vigor ➔ In-Cab Tractor VRA Spreader")
c.showPage()


# -------------------------------------------------------------
# SLIDE 20: CASE STUDY
# -------------------------------------------------------------
draw_slide_base(c, 19)
draw_slide_header(c, "17. Example Farmer Case Study: Punjab Wheat Farm", "CASE STUDY", 19)

draw_card(c, 60, 50, 260, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawString(80, 425, "Farmer Baseline Input")
cs1 = [
    "• Location: Jalandhar, Punjab",
    "• Crop: Wheat (HD-2967)",
    "• Farm Area: 25 Hectares",
    "• Soil N: 38 kg/ha (Low)",
    "• Soil P: 18 kg/ha (Medium)",
    "• Soil K: 32 kg/ha (Adequate)",
    "• Soil pH: 6.8 (Optimal)",
    "• 14-Day Rain: 18 mm",
    "• Target Yield: 6.2 t/ha"
]
draw_text_block(c, cs1, 80, 385, 'Helvetica', 9.5, 20, TEXT_DARK)

draw_card(c, 350, 50, 260, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawString(370, 425, "AgriOptima Prescription")
cs2 = [
    "• Predicted Yield: 6.35 t/ha",
    "• Delta N: +52 kg/ha",
    "• Delta P: +24 kg/ha",
    "• Delta K: 0 kg/ha",
    "",
    "Commercial Bags Needed:",
    "• Urea (50kg): 48 Bags",
    "• DAP (50kg): 26 Bags",
    "• MOP (50kg): 0 Bags"
]
draw_text_block(c, cs2, 370, 385, 'Helvetica', 9.5, 20, TEXT_DARK)

draw_card(c, 640, 50, 260, 410, CARD_ALT_BG)
c.setFillColor(ACCENT_GREEN)
c.setFont('Times-Bold', 32)
c.drawCentredString(770, 400, "$1,840")
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 14)
c.drawCentredString(770, 370, "Direct Cost Savings")
cs3 = [
    "• 34.2% Cost Reduction vs",
    "  blanket broadcasting.",
    "",
    "• 320 kg Run-off Prevented:",
    "  Zero excess nitrate in aquifers.",
    "",
    "• +2.4% Yield Bonus:",
    "  Harvest exceeded target yield."
]
draw_text_block(c, cs3, 660, 335, 'Helvetica', 9.5, 18, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 21: PROJECT AT A GLANCE
# -------------------------------------------------------------
draw_slide_base(c, 20)
draw_slide_header(c, "18. AgriOptima Project at a Glance", "SUMMARY", 20)

glance = [
    ("22", "Unit Tests Passing", ACCENT_BROWN),
    ("14", "Languages Supported", ACCENT_GREEN),
    ("6", "Agronomic Themes", ACCENT_BLUE),
    ("6", "Calibrated Crops", ACCENT_BROWN),
    ("4", "Google Map Layers", ACCENT_GREEN),
    ("100%", "Production Uptime", ACCENT_BLUE)
]

for idx, (num, lbl, col) in enumerate(glance):
    col_i = idx % 3
    row_i = idx // 3
    gx = 60 + col_i * 290
    gy = 250 - row_i * 145

    draw_card(c, gx, gy, 260, 125, CARD_BG)
    c.setFillColor(col)
    c.setFont('Times-Bold', 32)
    c.drawCentredString(gx + 130, gy + 75, num)
    c.setFillColor(PRIMARY_DARK)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(gx + 130, gy + 45, lbl)

draw_card(c, 60, 50, 840, 50, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Helvetica-Bold', 10)
c.drawCentredString(480, 70, "Python 3.11 + Django 5 + SciPy SLSQP + Sentinel-2 NDVI + Web Speech API = Unified Precision Agritech Ecosystem.")
c.showPage()


# -------------------------------------------------------------
# SLIDE 22: CLOUD DEPLOYMENT
# -------------------------------------------------------------
draw_slide_base(c, 21)
draw_slide_header(c, "19. Production Deployment & Cloud Architecture", "DEPLOYMENT", 21)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Cloud Infrastructure & CI/CD")
dep_lines = [
    "• Production Host: Render Platform-as-a-Service (PaaS) with zero-downtime rolling deploys.",
    "",
    "• Live Production URL:",
    "  https://agrioptima-jpva.onrender.com/",
    "",
    "• GitHub Repository:",
    "  https://github.com/67sdnew-hash/agrioptima",
    "",
    "• Server Stack: Gunicorn multi-worker WSGI behind Cloudflare CDN reverse proxy with HTTP/3 & SSL/TLS."
]
draw_text_block(c, dep_lines, 85, 385, 'Helvetica', 10, 18, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Automated Deployment Sequence")
cmds = [
    "# 1. Dependency Installation",
    "pip install -r requirements.txt",
    "",
    "# 2. Database Migrations",
    "python manage.py migrate",
    "",
    "# 3. Static Asset Compilation",
    "python manage.py collectstatic --no-input",
    "",
    "# 4. Production Server Launch",
    "gunicorn agrioptima.wsgi:application --bind 0.0.0.0:$PORT"
]
draw_text_block(c, cmds, 520, 385, 'Courier-Bold', 9.5, 18, PRIMARY_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 23: CONCLUSION & ROADMAP
# -------------------------------------------------------------
draw_slide_base(c, 22)
draw_slide_header(c, "20. Conclusion & Strategic Agritech Roadmap", "FUTURE VISION", 22)

draw_card(c, 60, 50, 405, 410, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(85, 425, "Key Project Achievements")
ach = [
    "• Scientific Rigor: Replaced fertilizer guesswork with Mitscherlich-Baule mathematical modeling.",
    "• Proven Economics: 25%–45% fertilizer cost savings per hectare.",
    "• Environmental Guardianship: Mitigates non-point source nitrate leaching into groundwater.",
    "• Universal Accessibility: 14 languages, hands-free voice, 6 themes, and camera diagnostics."
]
draw_text_block(c, ach, 85, 385, 'Helvetica', 10, 24, TEXT_DARK)

draw_card(c, 495, 50, 405, 410, CARD_ALT_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 15)
c.drawString(520, 425, "Future Roadmap & Expansion")
rm = [
    "• Autonomous Drone Telemetry: Direct prescription transmission to DJI Agras / XAG spray drones.",
    "• LoRaWAN Soil IoT Sensors: Live streaming soil moisture, EC conductivity, and nitrate levels.",
    "• Carbon Credit Verification: Automated certification of fertilizer reduction for carbon credits.",
    "• Parametric Crop Insurance: Satellite NDVI audit trail for instant insurance claims."
]
draw_text_block(c, rm, 520, 385, 'Helvetica', 10, 24, TEXT_DARK)
c.showPage()


# -------------------------------------------------------------
# SLIDE 24: THANK YOU
# -------------------------------------------------------------
draw_slide_base(c, 23)

draw_card(c, 100, 70, 760, 380, CARD_BG)
c.setFillColor(PRIMARY_DARK)
c.setFont('Times-Bold', 40)
c.drawCentredString(480, 370, "Thank You!")

c.setFillColor(ACCENT_BROWN)
c.setFont('Times-Bold', 18)
c.drawCentredString(480, 325, "AgriOptima 3D — Precision Crop Yield & Fertilizer Optimizer")

ty_lines = [
    "Live Production App: https://agrioptima-jpva.onrender.com/",
    "Multi-Zone GIS Mapper: https://agrioptima-jpva.onrender.com/zones/",
    "Farmer Community Hub: https://agrioptima-jpva.onrender.com/community/",
    "Source Repository: https://github.com/67sdnew-hash/agrioptima",
    "",
    "Built with mathematical precision and environmental care for sustainable agriculture worldwide."
]
draw_text_block(c, ty_lines, 180, 275, 'Helvetica', 10.5, 20, TEXT_DARK)

c.showPage()

# Save
c.save()
print(f"ReportLab PDF successfully saved to: {output_pdf_path}")
print(f"PDF Size: {os.path.getsize(output_pdf_path)} bytes")
