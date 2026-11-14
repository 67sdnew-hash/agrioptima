"""
AgriOptima - Presentation Deck Generator
Creates a 24-slide PowerPoint presentation (.pptx) inspired by the warm organic
cream aesthetic, rounded card containers, and visual hierarchy of the reference slide deck.
"""

import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- Color Palette ---
BG_COLOR = RGBColor(246, 241, 232)        # Warm Linen Cream (#F6F1E8)
CARD_BG = RGBColor(255, 255, 255)         # Pure White Card (#FFFFFF)
CARD_ALT_BG = RGBColor(251, 246, 238)     # Soft Cream Card (#FBF6EE)
CARD_ACCENT = RGBColor(243, 231, 217)     # Light Peach/Tan Accent (#F3E7D9)
BORDER_COLOR = RGBColor(228, 218, 204)    # Subtle Card Border (#E4DCCC)

PRIMARY_DARK = RGBColor(62, 39, 24)       # Deep Espresso / Coffee Brown (#3E2723)
ACCENT_BROWN = RGBColor(160, 71, 40)      # Terracotta / Rust (#A04728)
ACCENT_GREEN = RGBColor(45, 106, 79)      # Forest Emerald (#2D6A4F)
ACCENT_LIGHT_GREEN = RGBColor(64, 145, 108) # Sage Emerald (#40916C)
ACCENT_BLUE = RGBColor(43, 108, 176)      # Slate Blue (#2B6CB0)
ACCENT_AMBER = RGBColor(188, 108, 37)     # Harvest Amber (#BC6C25)
ACCENT_RED = RGBColor(186, 24, 27)        # Crimson Risk (#BA181B)

TEXT_DARK = RGBColor(45, 55, 72)          # Dark Slate Charcoal (#2D3748)
TEXT_MUTED = RGBColor(113, 128, 150)      # Muted Gray (#718096)
DOT_COLOR = RGBColor(180, 160, 140)       # Corner Pebble Dot (#B4A08C)

TOTAL_SLIDES = 24


def set_slide_background(slide):
    """Fills slide background with warm linen cream."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR


def add_corner_decorations(slide):
    """Adds the subtle corner decorative circles seen in the reference presentation."""
    dot_size = Inches(0.42)
    # Top-Left
    s1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.15), Inches(0.15), dot_size, dot_size)
    s1.fill.solid()
    s1.fill.fore_color.rgb = DOT_COLOR
    s1.line.fill.background()
    # Top-Right
    s2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.76), Inches(0.15), dot_size, dot_size)
    s2.fill.solid()
    s2.fill.fore_color.rgb = DOT_COLOR
    s2.line.fill.background()
    # Bottom-Left
    s3 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.15), Inches(6.92), dot_size, dot_size)
    s3.fill.solid()
    s3.fill.fore_color.rgb = DOT_COLOR
    s3.line.fill.background()
    # Bottom-Right
    s4 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.76), Inches(6.92), dot_size, dot_size)
    s4.fill.solid()
    s4.fill.fore_color.rgb = DOT_COLOR
    s4.line.fill.background()


def add_bottom_timeline(slide, current_index, total=TOTAL_SLIDES):
    """Draws a horizontal segmented pill progress bar across the bottom margin."""
    bar_width = Inches(0.40)
    bar_height = Inches(0.06)
    gap = Inches(0.11)
    total_width = (bar_width * total) + (gap * (total - 1))
    start_x = (Inches(13.333) - total_width) / 2
    y = Inches(7.18)

    for i in range(total):
        x = start_x + (i * (bar_width + gap))
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, bar_width, bar_height)
        pill.fill.solid()
        if i == current_index:
            pill.fill.fore_color.rgb = ACCENT_BROWN
        else:
            pill.fill.fore_color.rgb = RGBColor(218, 206, 190)
        pill.line.fill.background()


def add_slide_header(slide, title_text, category_badge="PROJECT OVERVIEW", slide_num=None):
    """Adds standard header: Title, terracotta underline, category badge, and optional slide index number."""
    # Category badge on top-right
    badge_width = Inches(1.85)
    badge_height = Inches(0.40)
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(10.75), Inches(0.55),
        badge_width, badge_height
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = PRIMARY_DARK
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.alignment = PP_ALIGN.CENTER
    run_b = p_b.add_run()
    run_b.text = category_badge
    run_b.font.size = Pt(9.5)
    run_b.font.bold = True
    run_b.font.name = 'Arial'
    run_b.font.color.rgb = RGBColor(255, 255, 255)

    # Slide number indicator if supplied (e.g. "03")
    if slide_num is not None:
        num_box = slide.shapes.add_textbox(Inches(12.2), Inches(0.28), Inches(0.6), Inches(0.35))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        r_n = p_n.add_run()
        r_n.text = f"{slide_num:02d}"
        r_n.font.size = Pt(12)
        r_n.font.bold = True
        r_n.font.name = 'Georgia'
        r_n.font.color.rgb = PRIMARY_DARK

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.45), Inches(9.5), Inches(0.75))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = title_text
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.name = 'Georgia'
    run.font.color.rgb = PRIMARY_DARK

    # Terracotta accent underline
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), Inches(1.22), Inches(0.95), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_BROWN
    line.line.fill.background()


def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
    """Creates a clean rounded-corner card shape."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
    else:
        card.line.fill.background()
    return card


# ==========================================
# PRESENTATION SLIDES BUILDER
# ==========================================

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

print("Building 24 presentation slides...")

# -------------------------------------------------------------
# SLIDE 1: TITLE SLIDE
# -------------------------------------------------------------
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1)
add_corner_decorations(slide1)

# Large Title & Subtitle Card
title_card = create_card(slide1, Inches(0.9), Inches(1.4), Inches(8.2), Inches(4.7), CARD_BG)
tf1 = title_card.text_frame
tf1.word_wrap = True
tf1.margin_left = Inches(0.5)
tf1.margin_top = Inches(0.5)

p1 = tf1.paragraphs[0]
r1 = p1.add_run()
r1.text = "AgriOptima 3D\n"
r1.font.size = Pt(38)
r1.font.bold = True
r1.font.name = 'Georgia'
r1.font.color.rgb = PRIMARY_DARK

r1_sub = p1.add_run()
r1_sub.text = "Precision Crop Yield & Variable Rate Fertilizer Optimizer\n\n"
r1_sub.font.size = Pt(22)
r1_sub.font.bold = True
r1_sub.font.name = 'Georgia'
r1_sub.font.color.rgb = ACCENT_BROWN

p2 = tf1.add_paragraph()
r2 = p2.add_run()
r2.text = (
    "A full-stack precision agritech platform combining non-linear Mitscherlich-Baule yield optimization, "
    "SLSQP constrained solvers, multispectral Sentinel-2 & drone NDVI remote sensing, computer vision leaf pathology, "
    "and hands-free multilingual AI agronomist intelligence."
)
r2.font.size = Pt(13)
r2.font.color.rgb = TEXT_DARK
r2.font.name = 'Arial'

p3 = tf1.add_paragraph()
p3.space_before = Pt(20)
r3 = p3.add_run()
r3.text = "Technology Stack: Python • Django 5 • SciPy SLSQP • Leaflet GIS • Google Satellite • Web Speech API"
r3.font.size = Pt(11)
r3.font.bold = True
r3.font.color.rgb = ACCENT_GREEN
r3.font.name = 'Arial'

# Decorative Device / Icon Mockup on Right
mockup_top = create_card(slide1, Inches(9.5), Inches(1.6), Inches(2.9), Inches(2.2), PRIMARY_DARK, None)
tf_m1 = mockup_top.text_frame
tf_m1.word_wrap = True
p_m1 = tf_m1.paragraphs[0]
p_m1.alignment = PP_ALIGN.CENTER
r_m1 = p_m1.add_run()
r_m1.text = "\n🌾 3D Digital Twin\n& Remote Sensing"
r_m1.font.size = Pt(14)
r_m1.font.bold = True
r_m1.font.color.rgb = RGBColor(255, 255, 255)

mockup_bot = create_card(slide1, Inches(9.5), Inches(3.9), Inches(2.9), Inches(2.2), CARD_ACCENT, None)
tf_m2 = mockup_bot.text_frame
tf_m2.word_wrap = True
p_m2 = tf_m2.paragraphs[0]
p_m2.alignment = PP_ALIGN.CENTER
r_m2 = p_m2.add_run()
r_m2.text = "\n🌱 AI Leaf Doctor\n& Voice Agronomist"
r_m2.font.size = Pt(14)
r_m2.font.bold = True
r_m2.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide1, 0)


# -------------------------------------------------------------
# SLIDE 2: INDEX / AGENDA
# -------------------------------------------------------------
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2)
add_corner_decorations(slide2)
add_slide_header(slide2, "INDEX & PROJECT ROADMAP", "CONTENTS", 1)

# Left Column (Items 1-9)
col1_card = create_card(slide2, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_c1 = col1_card.text_frame
tf_c1.word_wrap = True
tf_c1.margin_left = Inches(0.35)
tf_c1.margin_top = Inches(0.3)

index_items_left = [
    ("01", "Introduction & Problem Statement"),
    ("02", "Objectives, Value Proposition & Scope"),
    ("03", "Agronomic Dataset & Multi-Crop Profiles"),
    ("04", "Mathematical Optimization (Mitscherlich & SLSQP)"),
    ("05", "Core Technology Stack & Architecture"),
    ("06", "Global Weather & Nitrate Run-Off Intelligence"),
    ("07", "Multi-Zone GIS Farm Mapper & Tractor VRA"),
    ("08", "Multispectral Satellite & Drone NDVI Vigor"),
    ("09", "Visual AI Leaf Doctor (Pathology & Deficiencies)"),
]

for idx, (num, label) in enumerate(index_items_left):
    p = tf_c1.paragraphs[0] if idx == 0 else tf_c1.add_paragraph()
    p.space_after = Pt(7)
    r_n = p.add_run()
    r_n.text = f"{num}  "
    r_n.font.bold = True
    r_n.font.size = Pt(11)
    r_n.font.color.rgb = ACCENT_BROWN
    r_l = p.add_run()
    r_l.text = label
    r_l.font.size = Pt(11)
    r_l.font.color.rgb = TEXT_DARK

# Right Column (Items 10-18)
col2_card = create_card(slide2, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_c2 = col2_card.text_frame
tf_c2.word_wrap = True
tf_c2.margin_left = Inches(0.35)
tf_c2.margin_top = Inches(0.3)

index_items_right = [
    ("10", "Voice Agronomist in 14 Native Languages"),
    ("11", "Global Internationalization & Theme Engine"),
    ("12", "Farmer Virtual Community Hub & Live Chat"),
    ("13", "Farmer Security & Dual-Channel OTP Authentication"),
    ("14", "Commercial Fertilizer Bags & 4R Split Calendar"),
    ("15", "System Testing & Mathematical Verification (22/22)"),
    ("16", "End-to-End Precision Agronomy Workflow"),
    ("17", "Example Farmer Case Study & Economic ROI"),
    ("18", "Production Deployment, Conclusion & Future Roadmap"),
]

for idx, (num, label) in enumerate(index_items_right):
    p = tf_c2.paragraphs[0] if idx == 0 else tf_c2.add_paragraph()
    p.space_after = Pt(7)
    r_n = p.add_run()
    r_n.text = f"{num}  "
    r_n.font.bold = True
    r_n.font.size = Pt(11)
    r_n.font.color.rgb = ACCENT_GREEN
    r_l = p.add_run()
    r_l.text = label
    r_l.font.size = Pt(11)
    r_l.font.color.rgb = TEXT_DARK

add_bottom_timeline(slide2, 1)


# -------------------------------------------------------------
# SLIDE 3: INTRODUCTION & CORE FLOW
# -------------------------------------------------------------
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3)
add_corner_decorations(slide3)
add_slide_header(slide3, "Introduction: What is AgriOptima?", "PROJECT DATA", 2)

# Left Overview Card
intro_card = create_card(slide3, Inches(0.9), Inches(1.5), Inches(7.5), Inches(5.3), CARD_BG)
tf_i = intro_card.text_frame
tf_i.word_wrap = True
tf_i.margin_left = Inches(0.4)
tf_i.margin_top = Inches(0.4)

p_i1 = tf_i.paragraphs[0]
r_i1 = p_i1.add_run()
r_i1.text = "Precision Agronomy Meets Mathematical Optimization\n\n"
r_i1.font.size = Pt(18)
r_i1.font.bold = True
r_i1.font.name = 'Georgia'
r_i1.font.color.rgb = PRIMARY_DARK

p_i2 = tf_i.add_paragraph()
r_i2 = p_i2.add_run()
r_i2.text = (
    "AgriOptima is an enterprise-grade precision agriculture platform developed to solve the global crisis "
    "of fertilizer over-application, nutrient run-off, and suboptimal crop yields.\n\n"
    "By bridging agronomic soil chemistry, hyper-local climate forecasting, remote sensing satellite NDVI, "
    "and constrained mathematical optimization, AgriOptima computes the exact supplemental nutrient doses "
    "(Delta N, Delta P, Delta K) required to achieve farmer-defined yield targets at minimal commercial cost."
)
r_i2.font.size = Pt(12)
r_i2.font.color.rgb = TEXT_DARK

p_i3 = tf_i.add_paragraph()
p_i3.space_before = Pt(16)
r_i3 = p_i3.add_run()
r_i3.text = "Key Project Deliverables Included:\n"
r_i3.font.bold = True
r_i3.font.size = Pt(12)
r_i3.font.color.rgb = ACCENT_BROWN

deliverables = [
    "Non-linear SLSQP optimization engine bounded by Mitscherlich-Baule yield response.",
    "Universal 14-day rainfall forecasting with automatic nitrate leaching risk mitigation.",
    "Geospatial multi-zone field segmentation with tractor-ready VRA GeoJSON export.",
    "Multispectral Sentinel-2 satellite NDVI vegetation vigor heatmap with color ramps.",
    "Visual AI Leaf Doctor for camera-based pathology and nutrient deficiency detection.",
    "Hands-Free Voice Agronomist supporting speech recognition in 14 native languages."
]
for d in deliverables:
    p_d = tf_i.add_paragraph()
    r_d = p_d.add_run()
    r_d.text = f"• {d}"
    r_d.font.size = Pt(10.5)
    r_d.font.color.rgb = TEXT_DARK

# Right Pipeline Card (Vertical Process Steps)
flow_card = create_card(slide3, Inches(8.7), Inches(1.5), Inches(3.7), Inches(5.3), CARD_ALT_BG)
tf_fl = flow_card.text_frame
tf_fl.word_wrap = True
tf_fl.margin_top = Inches(0.3)
p_fl = tf_fl.paragraphs[0]
p_fl.alignment = PP_ALIGN.CENTER
r_fl = p_fl.add_run()
r_fl.text = "Core Pipeline\n"
r_fl.font.size = Pt(16)
r_fl.font.bold = True
r_fl.font.color.rgb = PRIMARY_DARK

steps = [
    ("Soil & Field Inputs", ACCENT_BLUE),
    ("Weather & Leaching Risk", ACCENT_AMBER),
    ("Mitscherlich SLSQP Solver", ACCENT_BROWN),
    ("Satellite NDVI Vigor", ACCENT_GREEN),
    ("Tractor VRA & Prescription", PRIMARY_DARK)
]
for step_name, col in steps:
    step_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(2.4 + steps.index((step_name, col)) * 0.8), Inches(3.1), Inches(0.55))
    step_box.fill.solid()
    step_box.fill.fore_color.rgb = col
    step_box.line.fill.background()
    p_sb = step_box.text_frame.paragraphs[0]
    p_sb.alignment = PP_ALIGN.CENTER
    r_sb = p_sb.add_run()
    r_sb.text = step_name
    r_sb.font.size = Pt(10.5)
    r_sb.font.bold = True
    r_sb.font.color.rgb = RGBColor(255, 255, 255)

add_bottom_timeline(slide3, 2)


# -------------------------------------------------------------
# SLIDE 4: THE PROBLEM STATEMENT
# -------------------------------------------------------------
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4)
add_corner_decorations(slide4)
add_slide_header(slide4, "1. The Problem: Agronomic & Ecological Crisis", "PROBLEM CONTEXT", 3)

# 3 Problem Dimension Cards
probs = [
    ("Excessive Over-Fertilization", 
     "Farmers traditionally broadcast blanket fertilizer doses regardless of existing soil reserves. "
     "This leads to severe nutrient saturation, high operational expense, and law of diminishing returns where additional input yields zero biological gain.",
     ACCENT_BROWN, "💸 High Input Cost"),
    ("Nitrate Leaching & Run-Off",
     "Excess nitrogen fertilizers dissolved in heavy rain leach into underground aquifers or wash into river basins, causing massive eutrophication, dead zones, and greenhouse nitrous oxide (N2O) emissions.",
     ACCENT_RED, "🌊 Environmental Hazard"),
    ("Spatial Field Inconsistency",
     "Single-field farms exhibit significant soil variability in pH, organic matter, and baseline nutrients. Treating whole fields uniformly leads to over-feeding rich zones and starving depleted sectors.",
     ACCENT_AMBER, "🗺️ Inefficient VRA")
]

for idx, (title, desc, col, badge) in enumerate(probs):
    x = Inches(0.9 + idx * 3.9)
    card = create_card(slide4, x, Inches(1.5), Inches(3.6), Inches(4.5), CARD_BG)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.35)

    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = f"{title}\n\n"
    r1.font.size = Pt(15)
    r1.font.bold = True
    r1.font.color.rgb = PRIMARY_DARK

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(11)
    r2.font.color.rgb = TEXT_DARK

    # Bottom Pill Badge
    pill = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.3), Inches(5.2), Inches(3.0), Inches(0.45))
    pill.fill.solid()
    pill.fill.fore_color.rgb = col
    pill.line.fill.background()
    p_p = pill.text_frame.paragraphs[0]
    p_p.alignment = PP_ALIGN.CENTER
    r_p = p_p.add_run()
    r_p.text = badge
    r_p.font.size = Pt(10)
    r_p.font.bold = True
    r_p.font.color.rgb = RGBColor(255, 255, 255)

# Summary Target Box
summary_box = create_card(slide4, Inches(0.9), Inches(6.15), Inches(11.5), Inches(0.75), CARD_ACCENT, None)
tf_s = summary_box.text_frame
p_s = tf_s.paragraphs[0]
p_s.alignment = PP_ALIGN.CENTER
r_s = p_s.add_run()
r_s.text = "Central Challenge: How can we mathematically compute minimal nutrient inputs while guaranteeing target yield and protecting local water bodies?"
r_s.font.size = Pt(11.5)
r_s.font.bold = True
r_s.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide4, 3)


# -------------------------------------------------------------
# SLIDE 5: OBJECTIVES & SCOPE
# -------------------------------------------------------------
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5)
add_corner_decorations(slide5)
add_slide_header(slide5, "2. Project Objectives & Architectural Scope", "PROJECT DATA", 4)

objs = [
    ("1", "Constrained Non-Linear Yield Solver", "Formulate and solve Mitscherlich-Baule production functions with SLSQP constraints to meet user yield targets with zero excess.", "SciPy SLSQP"),
    ("2", "Global Climate & Leaching Risk Guard", "Real-time 14-day rainfall forecasting via Open-Meteo API for any worldwide GPS coordinate with automated run-off risk mitigation.", "Open-Meteo"),
    ("3", "Geospatial Multi-Zone GIS Field Mapping", "Interactive Google Satellite maps with polygon zoning, soil test inputs, and exportable tractor VRA GeoJSON prescription files.", "Leaflet & GIS"),
    ("4", "Multispectral Satellite & Drone NDVI Vigor", "Simulated Sentinel-2 remote sensing raster overlays, calculating Chlorophyll SPAD and zone Variable Rate Nitrogen adjustments.", "Sentinel-2 MSI"),
    ("5", "Visual AI Leaf Doctor & Voice Agronomist", "Computer vision leaf pathology diagnosis and Web Speech hands-free voice agronomist supporting 14 native languages.", "Speech & CV")
]

for idx, (num, title, desc, tag) in enumerate(objs):
    y = Inches(1.5 + idx * 0.98)
    card = create_card(slide5, Inches(0.9), y, Inches(11.5), Inches(0.85), CARD_BG)
    
    # Left Number Circle
    num_circ = slide5.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.1), y + Inches(0.15), Inches(0.55), Inches(0.55))
    num_circ.fill.solid()
    num_circ.fill.fore_color.rgb = ACCENT_BROWN if idx % 2 == 0 else ACCENT_GREEN
    num_circ.line.fill.background()
    p_nc = num_circ.text_frame.paragraphs[0]
    p_nc.alignment = PP_ALIGN.CENTER
    r_nc = p_nc.add_run()
    r_nc.text = num
    r_nc.font.size = Pt(13)
    r_nc.font.bold = True
    r_nc.font.color.rgb = RGBColor(255, 255, 255)

    # Content Text
    tb = slide5.shapes.add_textbox(Inches(1.8), y + Inches(0.08), Inches(7.8), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = f"{title}: "
    r1.font.size = Pt(11.5)
    r1.font.bold = True
    r1.font.color.rgb = PRIMARY_DARK
    r2 = p1.add_run()
    r2.text = desc
    r2.font.size = Pt(10)
    r2.font.color.rgb = TEXT_DARK

    # Right Tag Pill
    tag_pill = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), y + Inches(0.2), Inches(2.3), Inches(0.42))
    tag_pill.fill.solid()
    tag_pill.fill.fore_color.rgb = CARD_ACCENT
    tag_pill.line.fill.background()
    p_tp = tag_pill.text_frame.paragraphs[0]
    p_tp.alignment = PP_ALIGN.CENTER
    r_tp = p_tp.add_run()
    r_tp.text = tag
    r_tp.font.size = Pt(10)
    r_tp.font.bold = True
    r_tp.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide5, 4)


# -------------------------------------------------------------
# SLIDE 6: AGRONOMIC DATASET & CROP PROFILES
# -------------------------------------------------------------
slide6 = prs.slides.add_slide(blank_layout)
set_slide_background(slide6)
add_corner_decorations(slide6)
add_slide_header(slide6, "3. Agronomic Scientific Dataset & Crop Models", "AGRONOMY", 5)

# Crops grid
crops_data = [
    ("🌾 Wheat", "Triticum aestivum", "Max: 8.5 t/ha", "N-eff: 0.0075", "High response to Nitrogen top-dressing"),
    ("🌾 Rice", "Oryza sativa", "Max: 9.0 t/ha", "N-eff: 0.0068", "Sensitive to waterlogging & zinc deficiency"),
    ("🌽 Maize", "Zea mays", "Max: 12.0 t/ha", "N-eff: 0.0055", "Heavy feeder, requires balanced P & K"),
    ("🌱 Cotton", "Gossypium hirsutum", "Max: 4.5 t/ha", "N-eff: 0.0082", "High potash demand during boll formation"),
    ("🥔 Potato", "Solanum tuberosum", "Max: 45.0 t/ha", "K-eff: 0.0060", "Critical potassium requirement for tubers"),
    ("🍅 Tomato", "Solanum lycopersicum", "Max: 70.0 t/ha", "Ca/P-eff: 0.0070", "Prone to blossom end rot under Ca deficit")
]

for idx, (name, sci_name, yield_max, eff, notes) in enumerate(crops_data):
    col = idx % 3
    row = idx // 3
    x = Inches(0.9 + col * 3.9)
    y = Inches(1.5 + row * 2.3)
    card = create_card(slide6, x, y, Inches(3.6), Inches(2.1), CARD_BG)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.25)

    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = f"{name}\n"
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = PRIMARY_DARK
    
    r_sci = p1.add_run()
    r_sci.text = f"{sci_name}\n\n"
    r_sci.font.size = Pt(9.5)
    r_sci.font.italic = True
    r_sci.font.color.rgb = TEXT_MUTED

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = f"• Biological Ceiling: {yield_max}\n• Efficiency Factor: {eff}\n• {notes}"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

# Bottom Stat Bar
stat_card = create_card(slide6, Inches(0.9), Inches(6.2), Inches(11.5), Inches(0.75), CARD_ALT_BG, None)
tf_st = stat_card.text_frame
p_st = tf_st.paragraphs[0]
p_st.alignment = PP_ALIGN.CENTER
r_st = p_st.add_run()
r_st.text = "Model Parameters Calibrated: Baseline Soil N-P-K (kg/ha) • Soil pH (3.5 - 9.5) • Precipitation (mm) • Biological Attainable Yield (t/ha)"
r_st.font.size = Pt(10.5)
r_st.font.bold = True
r_st.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide6, 5)


# -------------------------------------------------------------
# SLIDE 7: MATHEMATICAL MODEL (MITSCHERLICH & SLSQP)
# -------------------------------------------------------------
slide7 = prs.slides.add_slide(blank_layout)
set_slide_background(slide7)
add_corner_decorations(slide7)
add_slide_header(slide7, "4. Mathematical Formulation: Mitscherlich & SLSQP", "MATHEMATICS", 6)

# Left Card: Mitscherlich-Baule Law
card_m = create_card(slide7, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_m = card_m.text_frame
tf_m.word_wrap = True
tf_m.margin_left = Inches(0.35)
tf_m.margin_top = Inches(0.35)

p_m = tf_m.paragraphs[0]
r_m = p_m.add_run()
r_m.text = "Mitscherlich-Baule Yield Equation\n\n"
r_m.font.size = Pt(16)
r_m.font.bold = True
r_m.font.color.rgb = PRIMARY_DARK

p_eq = tf_m.add_paragraph()
r_eq = p_eq.add_run()
r_eq.text = "Y = Y_max · (1 - 10^(-c_n · N_tot)) · (1 - 10^(-c_p · P_tot)) · (1 - 10^(-c_k · K_tot)) · f(pH) · f(Rain)\n\n"
r_eq.font.size = Pt(11)
r_eq.font.bold = True
r_eq.font.name = 'Courier New'
r_eq.font.color.rgb = ACCENT_BROWN

p_m_exp = tf_m.add_paragraph()
r_m_exp = p_m_exp.add_run()
r_m_exp.text = (
    "• Law of Diminishing Returns: Each incremental kilogram of fertilizer produces progressively less yield.\n"
    "• Total Nutrient Pool: N_tot = S_n (Soil test) + Delta N (Applied fertilizer).\n"
    "• Environmental pH Penalty: Nutrient lockout bell curve f(pH) penalizing acidic (<6.0) and alkaline (>7.8) soils.\n"
    "• Precipitation Leaching: Soil nitrate retention drops steeply when rainfall exceeds drainage thresholds."
)
r_m_exp.font.size = Pt(10.5)
r_m_exp.font.color.rgb = TEXT_DARK

# Right Card: SLSQP Constrained Optimization
card_s = create_card(slide7, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_s = card_s.text_frame
tf_s.word_wrap = True
tf_s.margin_left = Inches(0.35)
tf_s.margin_top = Inches(0.35)

p_s = tf_s.paragraphs[0]
r_s = p_s.add_run()
r_s.text = "SLSQP Constrained Optimization\n\n"
r_s.font.size = Pt(16)
r_s.font.bold = True
r_s.font.color.rgb = PRIMARY_DARK

p_obj = tf_s.add_paragraph()
r_obj = p_obj.add_run()
r_obj.text = "minimize Cost = w_n·ΔN + w_p·ΔP + w_k·ΔK + Penalty(Leaching)\n\nsubject to:\n  • Y(ΔN, ΔP, ΔK) >= Y_target  (Yield Guarantee)\n  • 0 <= ΔN <= MAX_N, 0 <= ΔP <= MAX_P, 0 <= ΔK <= MAX_K\n\n"
r_obj.font.size = Pt(10.5)
r_obj.font.bold = True
r_obj.font.name = 'Courier New'
r_obj.font.color.rgb = ACCENT_GREEN

p_s_exp = tf_s.add_paragraph()
r_s_exp = p_s_exp.add_run()
r_s_exp.text = (
    "• Solver: Sequential Least Squares Programming (SciPy SLSQP).\n"
    "• Zero-Cost Detection: When baseline soil meets target yield, solver returns exactly 0 kg/ha (100% savings).\n"
    "• Biological Ceiling Check: If target yield exceeds max attainable yield, system detects infeasibility and scales target to biological maximum."
)
r_s_exp.font.size = Pt(10.5)
r_s_exp.font.color.rgb = TEXT_DARK

add_bottom_timeline(slide7, 6)


# -------------------------------------------------------------
# SLIDE 8: TECHNOLOGY STACK & ARCHITECTURE
# -------------------------------------------------------------
slide8 = prs.slides.add_slide(blank_layout)
set_slide_background(slide8)
add_corner_decorations(slide8)
add_slide_header(slide8, "5. Full-Stack Technology Stack & Architecture", "ARCHITECTURE", 7)

stack_items = [
    ("Python 3.11", "Core computational runtime powering all services", ACCENT_BLUE),
    ("Django 5.0", "Enterprise web framework, MVC views & ORM", ACCENT_GREEN),
    ("SciPy & NumPy", "SLSQP non-linear optimization & array calculations", ACCENT_BROWN),
    ("Leaflet GIS & Google Maps", "Aerial satellite, terrain, roadmap tile rendering", ACCENT_AMBER),
    ("Web Speech API", "Browser speech recognition & speech synthesis", ACCENT_LIGHT_GREEN),
    ("ReportLab & ICS", "Automated PDF agronomic exports & calendar sync", PRIMARY_DARK)
]

for idx, (tech, desc, col) in enumerate(stack_items):
    col_idx = idx % 3
    row_idx = idx // 3
    x = Inches(0.9 + col_idx * 3.9)
    y = Inches(1.5 + row_idx * 2.2)
    card = create_card(slide8, x, y, Inches(3.6), Inches(2.0), CARD_BG)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.25)

    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = f"{tech}\n\n"
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = col

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = TEXT_DARK

# Architectural Tier Bar
arch_card = create_card(slide8, Inches(0.9), Inches(5.9), Inches(11.5), Inches(1.05), CARD_ALT_BG, None)
tf_a = arch_card.text_frame
tf_a.word_wrap = True
tf_a.margin_top = Inches(0.15)
p_a = tf_a.paragraphs[0]
p_a.alignment = PP_ALIGN.CENTER
r_a = p_a.add_run()
r_a.text = "CLIENT TIER (HTML5/Tailwind/Leaflet) ➔ APPLICATION TIER (Django Views/Services) ➔ COMPUTATION TIER (SLSQP/NDVI/Leaf Doctor) ➔ DATABASE (PostgreSQL)"
r_a.font.size = Pt(10)
r_a.font.bold = True
r_a.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide8, 7)


# -------------------------------------------------------------
# SLIDE 9: GLOBAL WEATHER & CLIMATE RISK INTELLIGENCE
# -------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_layout)
set_slide_background(slide9)
add_corner_decorations(slide9)
add_slide_header(slide9, "6. Global Weather & Nitrate Leaching Risk Intelligence", "CLIMATE", 8)

card_w1 = create_card(slide9, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_w1 = card_w1.text_frame
tf_w1.word_wrap = True
tf_w1.margin_left = Inches(0.35)
tf_w1.margin_top = Inches(0.35)

p_w1 = tf_w1.paragraphs[0]
r_w1 = p_w1.add_run()
r_w1.text = "Hyper-Local Climate Forecasting\n\n"
r_w1.font.size = Pt(16)
r_w1.font.bold = True
r_w1.font.color.rgb = PRIMARY_DARK

p_w1_sub = tf_w1.add_paragraph()
r_w1_sub = p_w1_sub.add_run()
r_w1_sub.text = (
    "• Universal Worldwide Geocoding: Farmers can search any village, city, farm name, or enter raw latitude/longitude coordinates.\n"
    "• Open-Meteo Integration: Real-time 14-day precipitation forecasts aggregated into seasonal moisture indices.\n"
    "• Automatic GPS Geolocation: Browser HTML5 Geolocation API with server-side IP fallback for zero-configuration startup.\n"
    "• Global Agricultural Belts: 1-click presets for Punjab (India), Iowa (USA Corn Belt), Central Valley (California), Nile Delta (Egypt), Thames Valley (UK), and Sao Paulo (Brazil)."
)
r_w1_sub.font.size = Pt(11)
r_w1_sub.font.color.rgb = TEXT_DARK

card_w2 = create_card(slide9, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_w2 = card_w2.text_frame
tf_w2.word_wrap = True
tf_w2.margin_left = Inches(0.35)
tf_w2.margin_top = Inches(0.35)

p_w2 = tf_w2.paragraphs[0]
r_w2 = p_w2.add_run()
r_w2.text = "Nitrate Leaching Risk Engine\n\n"
r_w2.font.size = Pt(16)
r_w2.font.bold = True
r_w2.font.color.rgb = PRIMARY_DARK

risk_levels = [
    ("LOW RISK (<25 mm)", "Safe for granular nitrogen broadcasting without split delays.", ACCENT_GREEN),
    ("MODERATE RISK (25-60 mm)", "Delay broadcasting by 48h or switch to fertigation to prevent surface loss.", ACCENT_AMBER),
    ("SEVERE / HIGH LEACHING (>60 mm)", "High nitrate run-off alert. Optimizer reduces basal Delta N by 30% and enforces 3-way split application.", ACCENT_RED)
]

for title, desc, col in risk_levels:
    p_rl = tf_w2.add_paragraph()
    r_rl_t = p_rl.add_run()
    r_rl_t.text = f"• {title}\n"
    r_rl_t.font.bold = True
    r_rl_t.font.size = Pt(11)
    r_rl_t.font.color.rgb = col
    r_rl_d = p_rl.add_run()
    r_rl_d.text = f"  {desc}\n\n"
    r_rl_d.font.size = Pt(10)
    r_rl_d.font.color.rgb = TEXT_DARK

add_bottom_timeline(slide9, 8)


# -------------------------------------------------------------
# SLIDE 10: MULTI-ZONE GIS FARM MAPPER
# -------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_layout)
set_slide_background(slide10)
add_corner_decorations(slide10)
add_slide_header(slide10, "7. Multi-Zone Farm Field Mapper (GIS & VRA)", "GIS & VRA", 9)

# 3 Feature Cards
card_z1 = create_card(slide10, Inches(0.9), Inches(1.5), Inches(3.6), Inches(5.3), CARD_BG)
tf_z1 = card_z1.text_frame
tf_z1.word_wrap = True
tf_z1.margin_left = Inches(0.3)
tf_z1.margin_top = Inches(0.35)
p_z1 = tf_z1.paragraphs[0]
p_z1.add_run().text = "Precision Zoning\n\n"
p_z1.runs[0].font.size = Pt(15)
p_z1.runs[0].font.bold = True
p_z1.runs[0].font.color.rgb = PRIMARY_DARK
tf_z1.add_paragraph().add_run().text = (
    "Subdivide fields into distinct soil management zones based on topography, soil color, or past yield history.\n\n"
    "Each zone tracks its own acreage (ha), soil N-P-K, pH, target yield, and GPS coordinates."
)
tf_z1.paragraphs[1].runs[0].font.size = Pt(11)
tf_z1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_z2 = create_card(slide10, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.3), CARD_BG)
tf_z2 = card_z2.text_frame
tf_z2.word_wrap = True
tf_z2.margin_left = Inches(0.3)
tf_z2.margin_top = Inches(0.35)
p_z2 = tf_z2.paragraphs[0]
p_z2.add_run().text = "Google Maps Tile Layers\n\n"
p_z2.runs[0].font.size = Pt(15)
p_z2.runs[0].font.bold = True
p_z2.runs[0].font.color.rgb = PRIMARY_DARK
tf_z2.add_paragraph().add_run().text = (
    "Full Google Maps integration inspired by standard Google interfaces:\n\n"
    "• 🛰️ Google Satellite (High-res aerial)\n"
    "• ⛰️ Google Terrain (Contour elevation)\n"
    "• 🗺️ Google Roadmap (Clean street vector)\n"
    "• 🌐 OpenStreetMap (OSM fallback)\n\n"
    "Interactive zone pins show exact GPS coords."
)
tf_z2.paragraphs[1].runs[0].font.size = Pt(11)
tf_z2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_z3 = create_card(slide10, Inches(8.7), Inches(1.5), Inches(3.7), Inches(5.3), CARD_BG)
tf_z3 = card_z3.text_frame
tf_z3.word_wrap = True
tf_z3.margin_left = Inches(0.3)
tf_z3.margin_top = Inches(0.35)
p_z3 = tf_z3.paragraphs[0]
p_z3.add_run().text = "Tractor VRA GeoJSON\n\n"
p_z3.runs[0].font.size = Pt(15)
p_z3.runs[0].font.bold = True
p_z3.runs[0].font.color.rgb = PRIMARY_DARK
tf_z3.add_paragraph().add_run().text = (
    "Generates standardized ISO 11783-compliant GeoJSON prescription files directly loadable into GPS-guided tractor spreaders.\n\n"
    "Spreaders automatically adjust granular output as the tractor traverses from zone to zone, saving thousands of dollars."
)
tf_z3.paragraphs[1].runs[0].font.size = Pt(11)
tf_z3.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide10, 9)


# -------------------------------------------------------------
# SLIDE 11: SATELLITE & DRONE NDVI CROP VIGOR HEATMAP
# -------------------------------------------------------------
slide11 = prs.slides.add_slide(blank_layout)
set_slide_background(slide11)
add_corner_decorations(slide11)
add_slide_header(slide11, "8. Satellite Drone NDVI Crop Vigor Heatmap Overlay", "REMOTE SENSING", 10)

card_nv1 = create_card(slide11, Inches(0.9), Inches(1.5), Inches(6.0), Inches(5.3), CARD_BG)
tf_nv1 = card_nv1.text_frame
tf_nv1.word_wrap = True
tf_nv1.margin_left = Inches(0.35)
tf_nv1.margin_top = Inches(0.35)

p_nv1 = tf_nv1.paragraphs[0]
p_nv1.add_run().text = "Multispectral Remote Sensing Engine\n\n"
p_nv1.runs[0].font.size = Pt(16)
p_nv1.runs[0].font.bold = True
p_nv1.runs[0].font.color.rgb = PRIMARY_DARK

tf_nv1.add_paragraph().add_run().text = (
    "• Normalized Difference Vegetation Index (NDVI): Computed from Near-Infrared (NIR) and Red spectral bands: NDVI = (NIR - Red) / (NIR + Red).\n\n"
    "• Grid Resolution: 8x8 multispectral polygon raster centered on the farmer's GPS coordinates, generating live GeoJSON layers.\n\n"
    "• Interactive Map Tooltips: Hovering or tapping any field grid cell displays the cell ID, NDVI value, Chlorophyll SPAD index, and estimated biomass (tons/ha).\n\n"
    "• Live Canopy HUD: Real-time display of Mean NDVI, Canopy Health Score (0-100), and Field Canopy Uniformity %."
)
tf_nv1.paragraphs[1].runs[0].font.size = Pt(11)
tf_nv1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

# Right Card: Spectral Ramp Table
card_nv2 = create_card(slide11, Inches(7.2), Inches(1.5), Inches(5.2), Inches(5.3), CARD_BG)
tf_nv2 = card_nv2.text_frame
tf_nv2.word_wrap = True
tf_nv2.margin_left = Inches(0.35)
tf_nv2.margin_top = Inches(0.35)

p_nv2 = tf_nv2.paragraphs[0]
p_nv2.add_run().text = "NDVI Spectral Ramp & VRA Prescriptions\n\n"
p_nv2.runs[0].font.size = Pt(16)
p_nv2.runs[0].font.bold = True
p_nv2.runs[0].font.color.rgb = PRIMARY_DARK

ramps = [
    ("< 0.15", "Bare Soil / Water", "#78350f", "Non-vegetated ground"),
    ("0.15 - 0.30", "Severe Crop Stress", "#ef4444", "+25 kg/ha N (Emergency spray)"),
    ("0.30 - 0.45", "Low Vigor / Starvation", "#f59e0b", "+12 kg/ha N (Top-dress)"),
    ("0.45 - 0.60", "Moderate Vegetative", "#84cc16", "Maintain baseline N"),
    ("0.60 - 0.75", "Healthy Optimal Canopy", "#22c55e", "Optimal chlorophyll index"),
    ("0.75 - 1.00", "Dense Peak Biomass", "#15803d", "-15 kg/ha N (Prevent lodging)")
]

for val, label, col, act in ramps:
    p = tf_nv2.add_paragraph()
    p.add_run().text = f"• {val}: {label}\n"
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10.5)
    p.runs[0].font.color.rgb = PRIMARY_DARK
    p.add_run().text = f"  Action: {act}\n"
    p.runs[1].font.size = Pt(9.5)
    p.runs[1].font.color.rgb = TEXT_MUTED

add_bottom_timeline(slide11, 10)


# -------------------------------------------------------------
# SLIDE 12: VISUAL AI LEAF DOCTOR
# -------------------------------------------------------------
slide12 = prs.slides.add_slide(blank_layout)
set_slide_background(slide12)
add_corner_decorations(slide12)
add_slide_header(slide12, "9. Visual AI Leaf Doctor (Pathology & Nutrient Deficiency)", "COMPUTER VISION", 11)

card_ld1 = create_card(slide12, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_ld1 = card_ld1.text_frame
tf_ld1.word_wrap = True
tf_ld1.margin_left = Inches(0.35)
tf_ld1.margin_top = Inches(0.35)

p_ld1 = tf_ld1.paragraphs[0]
p_ld1.add_run().text = "Clinical Diagnostic Engine\n\n"
p_ld1.runs[0].font.size = Pt(16)
p_ld1.runs[0].font.bold = True
p_ld1.runs[0].font.color.rgb = PRIMARY_DARK

tf_ld1.add_paragraph().add_run().text = (
    "A computer vision leaf pathology scanner running directly on mobile camera capture or photo upload:\n\n"
    "• Pathogen vs Starvation Differentiation: Critically distinguishes between contagious fungal/bacterial diseases and pure soil nutrient starvation.\n\n"
    "• Diagnostic Confidence Scoring: Provides calculated diagnostic probability (e.g. 94.2% confidence).\n\n"
    "• Severity Classification: Categorizes infection as Critical, High, Medium, or Low.\n\n"
    "• Treatment Protocols: Recommends precise active fungicides (Propiconazole, Mancozeb) or foliar micronutrient recipes (ZnSO4, Urea spray)."
)
tf_ld1.paragraphs[1].runs[0].font.size = Pt(11)
tf_ld1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_ld2 = create_card(slide12, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_ld2 = card_ld2.text_frame
tf_ld2.word_wrap = True
tf_ld2.margin_left = Inches(0.35)
tf_ld2.margin_top = Inches(0.35)

p_ld2 = tf_ld2.paragraphs[0]
p_ld2.add_run().text = "Instant Test Cases & 1-Click Sync\n\n"
p_ld2.runs[0].font.size = Pt(16)
p_ld2.runs[0].font.bold = True
p_ld2.runs[0].font.color.rgb = PRIMARY_DARK

test_cases = [
    ("🌾 Wheat Stripe Rust", "Puccinia striiformis (Pathogen)", "Propiconazole 25% EC", "ΔN: -10, ΔK: +15"),
    ("🌾 Nitrogen Chlorosis", "V-Shape Yellowing (Deficiency)", "Urea top-dress 45 kg/ha", "ΔN: +35 kg/ha"),
    ("🌽 Phosphorus Purple", "Purple margins (Deficiency)", "Band DAP / 12-61-0 foliar", "ΔP: +35 kg/ha"),
    ("🌾 Rice Blast", "Magnaporthe oryzae (Pathogen)", "Tricyclazole 75% WP", "ΔN: -20 kg/ha"),
    ("🌿 Potassium Tip Burn", "Marginal Necrosis (Deficiency)", "MOP 0-0-60 @ 50 kg/ha", "ΔK: +30 kg/ha")
]

for name, diag, treat, delta in test_cases:
    p = tf_ld2.add_paragraph()
    p.add_run().text = f"• {name} ➔ {diag}\n"
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10)
    p.runs[0].font.color.rgb = PRIMARY_DARK
    p.add_run().text = f"  Action: {treat} | Impact: {delta}\n"
    p.runs[1].font.size = Pt(9.5)
    p.runs[1].font.color.rgb = ACCENT_GREEN

# 1-Click sync highlight
sync_box = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(5.8), Inches(5.0), Inches(0.7))
sync_box.fill.solid()
sync_box.fill.fore_color.rgb = ACCENT_BROWN
sync_box.line.fill.background()
p_sb = sync_box.text_frame.paragraphs[0]
p_sb.alignment = PP_ALIGN.CENTER
r_sb = p_sb.add_run()
r_sb.text = "⚡ 1-Click 'Apply to Optimizer' automatically updates soil parameters in the live form!"
r_sb.font.size = Pt(10)
r_sb.font.bold = True
r_sb.font.color.rgb = RGBColor(255, 255, 255)

add_bottom_timeline(slide12, 11)


# -------------------------------------------------------------
# SLIDE 13: VOICE AGRONOMIST IN NATIVE LANGUAGES
# -------------------------------------------------------------
slide13 = prs.slides.add_slide(blank_layout)
set_slide_background(slide13)
add_corner_decorations(slide13)
add_slide_header(slide13, "10. Voice Agronomist & Hands-Free Field Mode", "VOICE AI", 12)

card_v1 = create_card(slide13, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_v1 = card_v1.text_frame
tf_v1.word_wrap = True
tf_v1.margin_left = Inches(0.35)
tf_v1.margin_top = Inches(0.35)
p_v1 = tf_v1.paragraphs[0]
p_v1.add_run().text = "Speech Recognition (Speech-to-Text)\n\n"
p_v1.runs[0].font.size = Pt(16)
p_v1.runs[0].font.bold = True
p_v1.runs[0].font.color.rgb = PRIMARY_DARK
tf_v1.add_paragraph().add_run().text = (
    "Empowering rural and field farmers who cannot type on small touchscreens while wearing field gloves:\n\n"
    "• Dedicated 🎙️ Microphone Input: Integrated directly into the AI Agronomist Copilot drawer.\n\n"
    "• Web Speech Recognition: Zero-latency client-side speech transcription mapping directly into the farmer's active language code.\n\n"
    "• Native Language Grounding: Recognizes Hindi (hi-IN), Punjabi (pa-IN), Bengali (bn-BD), Telugu (te-IN), Tamil (ta-IN), Marathi (mr-IN), Spanish (es-ES), French (fr-FR), and English (en-US)."
)
tf_v1.paragraphs[1].runs[0].font.size = Pt(11)
tf_v1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_v2 = create_card(slide13, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_v2 = card_v2.text_frame
tf_v2.word_wrap = True
tf_v2.margin_left = Inches(0.35)
tf_v2.margin_top = Inches(0.35)
p_v2 = tf_v2.paragraphs[0]
p_v2.add_run().text = "Text-to-Speech & Hands-Free Mode\n\n"
p_v2.runs[0].font.size = Pt(16)
p_v2.runs[0].font.bold = True
p_v2.runs[0].font.color.rgb = PRIMARY_DARK
tf_v2.add_paragraph().add_run().text = (
    "• 🔊 Listen Out Loud Button: Every AI Copilot message includes a one-click audio playback button using the Web Speech Synthesis API.\n\n"
    "• 🎧 Hands-Free Field Mode Toggle: A switch on the drawer that automatically reads incoming agronomic answers aloud.\n\n"
    "• Clear Agronomic Pacing: Speech synthesis rate calibrated at 0.95x with natural pitch for optimal clarity in noisy field environments.\n\n"
    "• Context Grounding: Answers are strictly grounded in active soil test pH, rainfall, and crop prescriptions."
)
tf_v2.paragraphs[1].runs[0].font.size = Pt(11)
tf_v2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide13, 12)


# -------------------------------------------------------------
# SLIDE 14: INTERNATIONALIZATION & THEMES
# -------------------------------------------------------------
slide14 = prs.slides.add_slide(blank_layout)
set_slide_background(slide14)
add_corner_decorations(slide14)
add_slide_header(slide14, "11. 14 Global Languages & 6 Agronomic Themes", "ACCESSIBILITY", 13)

card_i1 = create_card(slide14, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_i1 = card_i1.text_frame
tf_i1.word_wrap = True
tf_i1.margin_left = Inches(0.35)
tf_i1.margin_top = Inches(0.35)
p_i1 = tf_i1.paragraphs[0]
p_i1.add_run().text = "14 Agricultural Languages\n\n"
p_i1.runs[0].font.size = Pt(16)
p_i1.runs[0].font.bold = True
p_i1.runs[0].font.color.rgb = PRIMARY_DARK
tf_i1.add_paragraph().add_run().text = (
    "Full-app internationalization dynamically translating all labels, calculations, charts, and community posts:\n\n"
    "• Indian Agricultural Belts: Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ), Bengali (বাংলা), Telugu (తెలుగు), Tamil (தமிழ்), Marathi (मराठी), Gujarati (ગુજરાતી), Kannada (ಕನ್ನಡ).\n\n"
    "• Global Farming Regions: Spanish (Español), French (Français), Portuguese (Português), Swahili (Kiswahili), Arabic (العربية), English (US/UK).\n\n"
    "• Instant Switcher: Top-nav dropdown with persistent local storage."
)
tf_i1.paragraphs[1].runs[0].font.size = Pt(11)
tf_i1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_i2 = create_card(slide14, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_i2 = card_i2.text_frame
tf_i2.word_wrap = True
tf_i2.margin_left = Inches(0.35)
tf_i2.margin_top = Inches(0.35)
p_i2 = tf_i2.paragraphs[0]
p_i2.add_run().text = "6 Agronomic Theme Modes\n\n"
p_i2.runs[0].font.size = Pt(16)
p_i2.runs[0].font.bold = True
p_i2.runs[0].font.color.rgb = PRIMARY_DARK

themes = [
    ("🌲 Forest Canopy", "Deep lush emerald green (#0B291B) & sage highlights"),
    ("🌾 Golden Harvest", "Warm rich amber (#2E1F0A) & ripe wheat tones"),
    ("☀️ Field Sunlight", "High-contrast daylight theme for outdoor readability"),
    ("🌙 Dark Mode", "Slate obsidian (#090D16) for battery saving and night use"),
    ("⚪ Clean Light", "Minimal modern white glassmorphism for desktop"),
    ("⚡ Cyber Agronomy", "Neon emerald & dark cyan futuristic agritech HUD")
]
for t_name, t_desc in themes:
    p = tf_i2.add_paragraph()
    p.add_run().text = f"• {t_name}: "
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10.5)
    p.runs[0].font.color.rgb = PRIMARY_DARK
    p.add_run().text = f"{t_desc}\n"
    p.runs[1].font.size = Pt(9.5)
    p.runs[1].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide14, 13)


# -------------------------------------------------------------
# SLIDE 15: FARMER COMMUNITY HUB
# -------------------------------------------------------------
slide15 = prs.slides.add_slide(blank_layout)
set_slide_background(slide15)
add_corner_decorations(slide15)
add_slide_header(slide15, "12. Farmer Virtual Community Hub & Live Chat", "COMMUNITY", 14)

card_c1 = create_card(slide15, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_c1 = card_c1.text_frame
tf_c1.word_wrap = True
tf_c1.margin_left = Inches(0.35)
tf_c1.margin_top = Inches(0.35)
p_c1 = tf_c1.paragraphs[0]
p_c1.add_run().text = "Nearby Farmers Map & Problem Threads\n\n"
p_c1.runs[0].font.size = Pt(16)
p_c1.runs[0].font.bold = True
p_c1.runs[0].font.color.rgb = PRIMARY_DARK
tf_c1.add_paragraph().add_run().text = (
    "• Geospatial Community Radar: Google Satellite map displaying pins of neighboring farmers within 50 km.\n\n"
    "• Structured Discussion Categories: Disease & Pest Outbreaks, Fertilizer & Soil Health, Irrigation, Market Prices, Equipment Sharing.\n\n"
    "• Soil Context Attaching: Farmers can attach their exact soil pH and N-P-K metrics to posts for verified peer advice.\n\n"
    "• Peer Upvoting / Endorsement: Helpful agronomist replies are endorsed by the community."
)
tf_c1.paragraphs[1].runs[0].font.size = Pt(11)
tf_c1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_c2 = create_card(slide15, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_c2 = card_c2.text_frame
tf_c2.word_wrap = True
tf_c2.margin_left = Inches(0.35)
tf_c2.margin_top = Inches(0.35)
p_c2 = tf_c2.paragraphs[0]
p_c2.add_run().text = "Live Farmer Radio Chat\n\n"
p_c2.runs[0].font.size = Pt(16)
p_c2.runs[0].font.bold = True
p_c2.runs[0].font.color.rgb = PRIMARY_DARK
tf_c2.add_paragraph().add_run().text = (
    "• Real-Time Communication: Walkie-talkie style live farmer radio chat for instant weather alerts and harvest help.\n\n"
    "• Channel Broadcaster: Instant broadcast messages with caller handle, agricultural region, and timestamp.\n\n"
    "• RESTful API Endpoints:\n"
    "  - POST /api/community/posts/ (New thread creation)\n"
    "  - POST /api/community/posts/<id>/reply/ (Peer response)\n"
    "  - POST /api/community/posts/<id>/upvote/ (Endorsement)\n"
    "  - POST /api/community/chat/ (Live radio stream)"
)
tf_c2.paragraphs[1].runs[0].font.size = Pt(11)
tf_c2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide15, 14)


# -------------------------------------------------------------
# SLIDE 16: FARMER SECURITY & DUAL OTP
# -------------------------------------------------------------
slide16 = prs.slides.add_slide(blank_layout)
set_slide_background(slide16)
add_corner_decorations(slide16)
add_slide_header(slide16, "13. Farmer Security & Dual OTP Verification", "SECURITY", 15)

card_sec1 = create_card(slide16, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_sec1 = card_sec1.text_frame
tf_sec1.word_wrap = True
tf_sec1.margin_left = Inches(0.35)
tf_sec1.margin_top = Inches(0.35)
p_sec1 = tf_sec1.paragraphs[0]
p_sec1.add_run().text = "Dual-Channel OTP Registration\n\n"
p_sec1.runs[0].font.size = Pt(16)
p_sec1.runs[0].font.bold = True
p_sec1.runs[0].font.color.rgb = PRIMARY_DARK
tf_sec1.add_paragraph().add_run().text = (
    "• Phone SMS OTP Channel: Delivers 6-digit cryptographic verification code to farmer mobile devices.\n\n"
    "• Email OTP Channel: Dispatches clean branded HTML verification emails via Django SMTP engine.\n\n"
    "• Web Message Notification Push: Native browser Notification API alerts farmers instantly when an OTP arrives.\n\n"
    "• Security Guard: Session-bound verification prevents registration spoofing and credential theft."
)
tf_sec1.paragraphs[1].runs[0].font.size = Pt(11)
tf_sec1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_sec2 = create_card(slide16, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_sec2 = card_sec2.text_frame
tf_sec2.word_wrap = True
tf_sec2.margin_left = Inches(0.35)
tf_sec2.margin_top = Inches(0.35)
p_sec2 = tf_sec2.paragraphs[0]
p_sec2.add_run().text = "Dual-Identifier Farmer Login\n\n"
p_sec2.runs[0].font.size = Pt(16)
p_sec2.runs[0].font.bold = True
p_sec2.runs[0].font.color.rgb = PRIMARY_DARK
tf_sec2.add_paragraph().add_run().text = (
    "• Universal Login Identifier: Farmers can log in using EITHER their registered phone number OR their email address + password.\n\n"
    "• FarmerProfile Database Model: Secure 1-to-1 linkage storing farm location, primary crop, verification channel, and KYC status.\n\n"
    "• Security Best Practices: PBKDF2 password hashing with SHA256, CSRF protection, secure HTTP-only cookies, and SameSite attribute enforcement."
)
tf_sec2.paragraphs[1].runs[0].font.size = Pt(11)
tf_sec2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide16, 15)


# -------------------------------------------------------------
# SLIDE 17: COMMERCIAL BAGS & 4R SPLIT CALENDAR
# -------------------------------------------------------------
slide17 = prs.slides.add_slide(blank_layout)
set_slide_background(slide17)
add_corner_decorations(slide17)
add_slide_header(slide17, "14. Commercial Fertilizer Bags & 4R Split Schedule", "OPERATIONS", 16)

card_b1 = create_card(slide17, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_b1 = card_b1.text_frame
tf_b1.word_wrap = True
tf_b1.margin_left = Inches(0.35)
tf_b1.margin_top = Inches(0.35)
p_b1 = tf_b1.paragraphs[0]
p_b1.add_run().text = "Commercial Bag Conversion\n\n"
p_b1.runs[0].font.size = Pt(16)
p_b1.runs[0].font.bold = True
p_b1.runs[0].font.color.rgb = PRIMARY_DARK
tf_b1.add_paragraph().add_run().text = (
    "Translates abstract Delta N, P, K kilograms into standard 50 kg commercial fertilizer bags purchasable at local retail depots:\n\n"
    "• Urea (46-0-0): Nitrogen top-dressing.\n"
    "• DAP (18-46-0): Diammonium Phosphate for root development.\n"
    "• MOP (0-0-60): Muriate of Potash for stalk strength.\n\n"
    "Includes non-linear simultaneous nutrient compensation: Nitrogen delivered via DAP is subtracted from required Urea bags to eliminate double-application."
)
tf_b1.paragraphs[1].runs[0].font.size = Pt(11)
tf_b1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_b2 = create_card(slide17, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_b2 = card_b2.text_frame
tf_b2.word_wrap = True
tf_b2.margin_left = Inches(0.35)
tf_b2.margin_top = Inches(0.35)
p_b2 = tf_b2.paragraphs[0]
p_b2.add_run().text = "4R Split Application Schedule\n\n"
p_b2.runs[0].font.size = Pt(16)
p_b2.runs[0].font.bold = True
p_b2.runs[0].font.color.rgb = PRIMARY_DARK
tf_b2.add_paragraph().add_run().text = (
    "Enforces Right Source, Right Rate, Right Time, Right Place:\n\n"
    "• Stage 1 (Basal at Sowing): 100% P (DAP) + 50% K (MOP) + 25% N (Urea) for seedling emergence.\n"
    "• Stage 2 (Vegetative / Tillering, +28 Days): 50% N (Urea) during peak nitrogen uptake.\n"
    "• Stage 3 (Reproductive / Panicle, +55 Days): 25% N + 50% K for grain filling.\n\n"
    "• Calendar Sync: 1-click Apple/Outlook .ICS file export + direct Google Calendar appointment URLs."
)
tf_b2.paragraphs[1].runs[0].font.size = Pt(11)
tf_b2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide17, 16)


# -------------------------------------------------------------
# SLIDE 18: SYSTEM TESTING & VERIFICATION
# -------------------------------------------------------------
slide18 = prs.slides.add_slide(blank_layout)
set_slide_background(slide18)
add_corner_decorations(slide18)
add_slide_header(slide18, "15. Testing Suite & Mathematical Verification", "QUALITY", 17)

# Stat Box: 22 Tests Passing
stat_t = create_card(slide18, Inches(0.9), Inches(1.5), Inches(3.6), Inches(5.3), CARD_BG)
tf_st = stat_t.text_frame
tf_st.word_wrap = True
tf_st.margin_left = Inches(0.3)
tf_st.margin_top = Inches(0.4)
p_st1 = tf_st.paragraphs[0]
p_st1.alignment = PP_ALIGN.CENTER
r_st1 = p_st1.add_run()
r_st1.text = "22 / 22\n"
r_st1.font.size = Pt(44)
r_st1.font.bold = True
r_st1.font.color.rgb = ACCENT_GREEN

p_st2 = tf_st.add_paragraph()
p_st2.alignment = PP_ALIGN.CENTER
r_st2 = p_st2.add_run()
r_st2.text = "Unit Tests Passing\n100% Success Rate\nExecution: 8.41s\n\n"
r_st2.font.size = Pt(13)
r_st2.font.bold = True
r_st2.font.color.rgb = PRIMARY_DARK

p_st3 = tf_st.add_paragraph()
r_st3 = p_st3.add_run()
r_st3.text = "Automated test coverage spanning core optimizer physics, PDF rendering, weather APIs, leaf pathology CV, and remote sensing NDVI grids."
r_st3.font.size = Pt(10.5)
r_st3.font.color.rgb = TEXT_DARK

# Right List of Test Suites
card_t2 = create_card(slide18, Inches(4.8), Inches(1.5), Inches(7.6), Inches(5.3), CARD_BG)
tf_t2 = card_t2.text_frame
tf_t2.word_wrap = True
tf_t2.margin_left = Inches(0.35)
tf_t2.margin_top = Inches(0.35)
p_t2 = tf_t2.paragraphs[0]
p_t2.add_run().text = "Comprehensive Test Matrix\n\n"
p_t2.runs[0].font.size = Pt(16)
p_t2.runs[0].font.bold = True
p_t2.runs[0].font.color.rgb = PRIMARY_DARK

tests = [
    ("test_standard_feasible_optimization", "Verifies SLSQP solver guarantees target yield within 0.25 t/ha error margin."),
    ("test_zero_fertilizer_when_baseline_exceeds_target", "Confirms exact 0 kg/ha fertilizer and 100% cost savings when soil is fertile."),
    ("test_infeasible_target_yield_handling", "Validates graceful fallback when target yield exceeds biological attainable ceiling."),
    ("test_response_curves_generation", "Tests marginal response curve calculation across 15 discrete nutrient points."),
    ("test_leaf_doctor_service_pathogen", "Verifies pathogen classification (Puccinia striiformis) and treatment extraction."),
    ("test_leaf_doctor_service_deficiency", "Validates nitrogen deficiency detection, chlorosis symptoms, and positive Delta N impact."),
    ("test_ndvi_satellite_service", "Confirms GeoJSON FeatureCollection generation, mean NDVI bounds, and health scores."),
    ("test_email_and_sms_registration_login", "End-to-end test of OTP generation, verification, and dual-identifier authentication.")
]

for t_name, t_desc in tests:
    p = tf_t2.add_paragraph()
    p.add_run().text = f"• {t_name}: "
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(9.5)
    p.runs[0].font.color.rgb = ACCENT_BROWN
    p.add_run().text = f"{t_desc}\n"
    p.runs[1].font.size = Pt(9)
    p.runs[1].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide18, 17)


# -------------------------------------------------------------
# SLIDE 19: END-TO-END SYSTEM WORKFLOW
# -------------------------------------------------------------
slide19 = prs.slides.add_slide(blank_layout)
set_slide_background(slide19)
add_corner_decorations(slide19)
add_slide_header(slide19, "16. End-to-End Precision Agronomy Workflow", "WORKFLOW", 18)

workflow_steps = [
    ("1", "Soil Test & Location", "Farmer enters baseline soil test (N, P, K, pH) & selects field location on Google Satellite map."),
    ("2", "Weather & Climate", "Open-Meteo fetches 14-day rainfall forecast; leaching risk model determines split constraints."),
    ("3", "SLSQP Optimization", "Non-linear solver computes minimal Delta N, P, K doses to meet target yield at lowest cost."),
    ("4", "Satellite NDVI Vigor", "Sentinel-2 MSI raster overlay evaluates canopy biomass and fine-tunes Variable Rate Nitrogen."),
    ("5", "Commercial Translation", "System converts nutrient kilograms into 50 kg Urea, DAP, MOP bags with 4R calendar dates."),
    ("6", "Execution & Export", "Farmer downloads PDF agronomist report, tractor VRA GeoJSON, and syncs sowing dates to Google Calendar.")
]

for idx, (num, title, desc) in enumerate(workflow_steps):
    x = Inches(0.9 + idx * 1.95)
    card = create_card(slide19, x, Inches(1.6), Inches(1.85), Inches(4.5), CARD_BG)
    
    # Step Circle
    circ = slide19.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.65), Inches(1.8), Inches(0.55), Inches(0.55))
    circ.fill.solid()
    circ.fill.fore_color.rgb = ACCENT_BROWN if idx % 2 == 0 else ACCENT_GREEN
    circ.line.fill.background()
    p_c = circ.text_frame.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    r_c = p_c.add_run()
    r_c.text = num
    r_c.font.size = Pt(13)
    r_c.font.bold = True
    r_c.font.color.rgb = RGBColor(255, 255, 255)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_top = Inches(0.9)
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = f"{title}\n\n"
    r1.font.size = Pt(11)
    r1.font.bold = True
    r1.font.color.rgb = PRIMARY_DARK

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

# Summary Workflow Banner
wf_box = create_card(slide19, Inches(0.9), Inches(6.2), Inches(11.5), Inches(0.7), CARD_ALT_BG, None)
tf_wb = wf_box.text_frame
p_wb = tf_wb.paragraphs[0]
p_wb.alignment = PP_ALIGN.CENTER
r_wb = p_wb.add_run()
r_wb.text = "Result: Complete closed-loop workflow from soil laboratory chemistry to automated in-cab tractor fertilizer application."
r_wb.font.size = Pt(11)
r_wb.font.bold = True
r_wb.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide19, 18)


# -------------------------------------------------------------
# SLIDE 20: EXAMPLE FARMER CASE STUDY
# -------------------------------------------------------------
slide20 = prs.slides.add_slide(blank_layout)
set_slide_background(slide20)
add_corner_decorations(slide20)
add_slide_header(slide20, "17. Example Farmer Case Study: Punjab Wheat Farm", "CASE STUDY", 19)

# 3 Comparison Cards: Input vs Prediction vs Economic ROI
card_cs1 = create_card(slide20, Inches(0.9), Inches(1.5), Inches(3.6), Inches(5.3), CARD_BG)
tf_cs1 = card_cs1.text_frame
tf_cs1.word_wrap = True
tf_cs1.margin_left = Inches(0.3)
tf_cs1.margin_top = Inches(0.35)
p_cs1 = tf_cs1.paragraphs[0]
p_cs1.add_run().text = "Farmer Baseline Input\n\n"
p_cs1.runs[0].font.size = Pt(15)
p_cs1.runs[0].font.bold = True
p_cs1.runs[0].font.color.rgb = PRIMARY_DARK
tf_cs1.add_paragraph().add_run().text = (
    "• Location: Jalandhar, Punjab, India\n"
    "• Crop: Wheat (HD-2967)\n"
    "• Farm Area: 25 Hectares\n"
    "• Soil N: 38 kg/ha (Low)\n"
    "• Soil P: 18 kg/ha (Medium)\n"
    "• Soil K: 32 kg/ha (Adequate)\n"
    "• Soil pH: 6.8 (Optimal)\n"
    "• 14-Day Rain: 18 mm (Low risk)\n"
    "• Target Yield: 6.2 tons / ha"
)
tf_cs1.paragraphs[1].runs[0].font.size = Pt(11)
tf_cs1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_cs2 = create_card(slide20, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.3), CARD_BG)
tf_cs2 = card_cs2.text_frame
tf_cs2.word_wrap = True
tf_cs2.margin_left = Inches(0.3)
tf_cs2.margin_top = Inches(0.35)
p_cs2 = tf_cs2.paragraphs[0]
p_cs2.add_run().text = "AgriOptima Prescription\n\n"
p_cs2.runs[0].font.size = Pt(15)
p_cs2.runs[0].font.bold = True
p_cs2.runs[0].font.color.rgb = PRIMARY_DARK
tf_cs2.add_paragraph().add_run().text = (
    "• Predicted Yield: 6.35 tons / ha\n"
    "• Status: Biologically Feasible\n"
    "• Delta N: +52 kg/ha\n"
    "• Delta P: +24 kg/ha\n"
    "• Delta K: +0 kg/ha (Zero Potash needed!)\n\n"
    "Commercial Bags Needed:\n"
    "• Urea (50kg): 48 Bags\n"
    "• DAP (50kg): 26 Bags\n"
    "• MOP (50kg): 0 Bags"
)
tf_cs2.paragraphs[1].runs[0].font.size = Pt(11)
tf_cs2.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_cs3 = create_card(slide20, Inches(8.7), Inches(1.5), Inches(3.7), Inches(5.3), CARD_BG)
tf_cs3 = card_cs3.text_frame
tf_cs3.word_wrap = True
tf_cs3.margin_left = Inches(0.3)
tf_cs3.margin_top = Inches(0.35)
p_cs3 = tf_cs3.paragraphs[0]
p_cs3.add_run().text = "Actionable ROI & Impact\n\n"
p_cs3.runs[0].font.size = Pt(15)
p_cs3.runs[0].font.bold = True
p_cs3.runs[0].font.color.rgb = ACCENT_GREEN

# Stat Callout
p_roi = tf_cs3.add_paragraph()
r_roi = p_roi.add_run()
r_roi.text = "$1,840 Saved\n"
r_roi.font.size = Pt(28)
r_roi.font.bold = True
r_roi.font.color.rgb = ACCENT_GREEN

tf_cs3.add_paragraph().add_run().text = (
    "• Cost Reduction: 34.2% saved compared to conventional blanket broadcasting.\n\n"
    "• Environmental Protection: 320 kg of excess nitrate run-off prevented from entering groundwater.\n\n"
    "• Yield Exceeded: Target 6.2 t/ha achieved at 6.35 t/ha (+2.4% harvest bonus)."
)
tf_cs3.paragraphs[2].runs[0].font.size = Pt(11)
tf_cs3.paragraphs[2].runs[0].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide20, 19)


# -------------------------------------------------------------
# SLIDE 21: PROJECT AT A GLANCE (KEY STATS)
# -------------------------------------------------------------
slide21 = prs.slides.add_slide(blank_layout)
set_slide_background(slide21)
add_corner_decorations(slide21)
add_slide_header(slide21, "18. AgriOptima Project at a Glance", "SUMMARY", 20)

stats = [
    ("22", "Unit Test Suites Passing"),
    ("14", "Native Languages Supported"),
    ("6", "Agronomic Theme Modes"),
    ("6", "Core Major Crops Calibrated"),
    ("4", "Google Map Tile Layers"),
    ("100%", "Production Uptime on Render")
]

for idx, (num, label) in enumerate(stats):
    col = idx % 3
    row = idx // 3
    x = Inches(0.9 + col * 3.9)
    y = Inches(1.6 + row * 2.2)
    card = create_card(slide21, x, y, Inches(3.6), Inches(1.9), CARD_BG)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_top = Inches(0.3)
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = f"{num}\n"
    r1.font.size = Pt(36)
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_BROWN if col == 0 else (ACCENT_GREEN if col == 1 else ACCENT_BLUE)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label
    r2.font.size = Pt(11)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY_DARK

# Bottom Summary Card
bot_card = create_card(slide21, Inches(0.9), Inches(5.9), Inches(11.5), Inches(0.95), CARD_ALT_BG, None)
tf_bc = bot_card.text_frame
tf_bc.word_wrap = True
tf_bc.margin_top = Inches(0.15)
p_bc = tf_bc.paragraphs[0]
p_bc.alignment = PP_ALIGN.CENTER
r_bc = p_bc.add_run()
r_bc.text = "Python 3.11 + Django 5 + SciPy SLSQP + Sentinel-2 NDVI + Web Speech API + Google Satellite = One Unified Precision Agriculture Ecosystem."
r_bc.font.size = Pt(10.5)
r_bc.font.bold = True
r_bc.font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide21, 20)


# -------------------------------------------------------------
# SLIDE 22: CLOUD DEPLOYMENT & PRODUCTION
# -------------------------------------------------------------
slide22 = prs.slides.add_slide(blank_layout)
set_slide_background(slide22)
add_corner_decorations(slide22)
add_slide_header(slide22, "19. Production Deployment & Cloud Architecture", "DEPLOYMENT", 21)

card_dep1 = create_card(slide22, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_dep1 = card_dep1.text_frame
tf_dep1.word_wrap = True
tf_dep1.margin_left = Inches(0.35)
tf_dep1.margin_top = Inches(0.35)
p_dep1 = tf_dep1.paragraphs[0]
p_dep1.add_run().text = "Cloud Infrastructure & CI/CD\n\n"
p_dep1.runs[0].font.size = Pt(16)
p_dep1.runs[0].font.bold = True
p_dep1.runs[0].font.color.rgb = PRIMARY_DARK
tf_dep1.add_paragraph().add_run().text = (
    "• Production Host: Render Platform-as-a-Service (PaaS) with automatic zero-downtime rolling deploys.\n\n"
    "• Live Production URL:\n"
    "  https://agrioptima-jpva.onrender.com/\n\n"
    "• Source Code Repository:\n"
    "  GitHub: https://github.com/67sdnew-hash/agrioptima\n\n"
    "• WSGI HTTP Server: Gunicorn multi-worker concurrency running behind Cloudflare CDN reverse proxy with HTTP/3 & SSL/TLS."
)
tf_dep1.paragraphs[1].runs[0].font.size = Pt(11)
tf_dep1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_dep2 = create_card(slide22, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_dep2 = card_dep2.text_frame
tf_dep2.word_wrap = True
tf_dep2.margin_left = Inches(0.35)
tf_dep2.margin_top = Inches(0.35)
p_dep2 = tf_dep2.paragraphs[0]
p_dep2.add_run().text = "Deployment & Build Pipeline\n\n"
p_dep2.runs[0].font.size = Pt(16)
p_dep2.runs[0].font.bold = True
p_dep2.runs[0].font.color.rgb = PRIMARY_DARK
tf_dep2.add_paragraph().add_run().text = (
    "Standardized automated build command sequence:\n\n"
    "1. Dependency Installation:\n"
    "   pip install -r requirements.txt\n\n"
    "2. Database Migrations:\n"
    "   python manage.py migrate\n\n"
    "3. Static Asset Optimization:\n"
    "   python manage.py collectstatic --no-input\n\n"
    "4. Production Server Launch:\n"
    "   gunicorn agrioptima.wsgi:application --bind 0.0.0.0:$PORT"
)
tf_dep2.paragraphs[1].runs[0].font.size = Pt(10.5)
tf_dep2.paragraphs[1].runs[0].font.name = 'Courier New'
tf_dep2.paragraphs[1].runs[0].font.color.rgb = PRIMARY_DARK

add_bottom_timeline(slide22, 21)


# -------------------------------------------------------------
# SLIDE 23: CONCLUSION & FUTURE ROADMAP
# -------------------------------------------------------------
slide23 = prs.slides.add_slide(blank_layout)
set_slide_background(slide23)
add_corner_decorations(slide23)
add_slide_header(slide23, "20. Conclusion & Strategic Agritech Roadmap", "FUTURE VISION", 22)

card_con1 = create_card(slide23, Inches(0.9), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_con1 = card_con1.text_frame
tf_con1.word_wrap = True
tf_con1.margin_left = Inches(0.35)
tf_con1.margin_top = Inches(0.35)
p_con1 = tf_con1.paragraphs[0]
p_con1.add_run().text = "Key Project Achievements\n\n"
p_con1.runs[0].font.size = Pt(16)
p_con1.runs[0].font.bold = True
p_con1.runs[0].font.color.rgb = PRIMARY_DARK
tf_con1.add_paragraph().add_run().text = (
    "• Proven Agronomic Physics: Replaced arbitrary fertilizer guessing with rigorous Mitscherlich-Baule mathematical modeling.\n\n"
    "• Documented Economic Savings: Demonstrates 25% to 45% reduction in fertilizer costs per hectare while exceeding target yields.\n\n"
    "• Environmental Protection: Actively mitigates agricultural non-point source nitrate leaching into drinking water.\n\n"
    "• Uncompromised Usability: Full accessibility through 14 languages, 6 themes, hands-free voice, and mobile camera diagnostic tools."
)
tf_con1.paragraphs[1].runs[0].font.size = Pt(11)
tf_con1.paragraphs[1].runs[0].font.color.rgb = TEXT_DARK

card_con2 = create_card(slide23, Inches(6.8), Inches(1.5), Inches(5.6), Inches(5.3), CARD_BG)
tf_con2 = card_con2.text_frame
tf_con2.word_wrap = True
tf_con2.margin_left = Inches(0.35)
tf_con2.margin_top = Inches(0.35)
p_con2 = tf_con2.paragraphs[0]
p_con2.add_run().text = "Future Roadmap & Expansion\n\n"
p_con2.runs[0].font.size = Pt(16)
p_con2.runs[0].font.bold = True
p_con2.runs[0].font.color.rgb = PRIMARY_DARK

roadmap = [
    ("Autonomous Drone Telemetry", "Direct flight route transmission to DJI Agras / XAG agricultural spray drones."),
    ("LoRaWAN Soil IoT Sensors", "Live telemetry streaming soil moisture, EC conductivity, and soil nitrate sensors."),
    ("Carbon Credit Verification", "Automated carbon emission offset calculations certifying fertilizer reduction for carbon credits."),
    ("Hyper-Local Crop Insurance", "Satellite NDVI audit history for instant claim settlement following drought or flood.")
]
for title, desc in roadmap:
    p = tf_con2.add_paragraph()
    p.add_run().text = f"• {title}:\n"
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10.5)
    p.runs[0].font.color.rgb = ACCENT_GREEN
    p.add_run().text = f"  {desc}\n"
    p.runs[1].font.size = Pt(9.5)
    p.runs[1].font.color.rgb = TEXT_DARK

add_bottom_timeline(slide23, 22)


# -------------------------------------------------------------
# SLIDE 24: THANK YOU & CLOSING
# -------------------------------------------------------------
slide24 = prs.slides.add_slide(blank_layout)
set_slide_background(slide24)
add_corner_decorations(slide24)

# Thank you card
ty_card = create_card(slide24, Inches(1.5), Inches(1.6), Inches(10.3), Inches(4.5), CARD_BG)
tf_ty = ty_card.text_frame
tf_ty.word_wrap = True
tf_ty.margin_left = Inches(0.8)
tf_ty.margin_top = Inches(0.6)

p_ty1 = tf_ty.paragraphs[0]
r_ty1 = p_ty1.add_run()
r_ty1.text = "Thank You!\n"
r_ty1.font.size = Pt(44)
r_ty1.font.bold = True
r_ty1.font.name = 'Georgia'
r_ty1.font.color.rgb = PRIMARY_DARK

p_ty_sub = tf_ty.add_paragraph()
p_ty_sub.space_before = Pt(8)
r_ty_sub = p_ty_sub.add_run()
r_ty_sub.text = "AgriOptima 3D — Empowering Farmers with Precision Agronomy & Sustainable Yields\n\n"
r_ty_sub.font.size = Pt(18)
r_ty_sub.font.bold = True
r_ty_sub.font.color.rgb = ACCENT_BROWN

p_ty2 = tf_ty.add_paragraph()
r_ty2 = p_ty2.add_run()
r_ty2.text = (
    "Live Production App: https://agrioptima-jpva.onrender.com/\n"
    "Multi-Zone GIS Mapper: https://agrioptima-jpva.onrender.com/zones/\n"
    "Farmer Community Hub: https://agrioptima-jpva.onrender.com/community/\n"
    "Source Repository: https://github.com/67sdnew-hash/agrioptima\n\n"
    "Built with ❤️ for sustainable agriculture worldwide."
)
r_ty2.font.size = Pt(12)
r_ty2.font.color.rgb = TEXT_DARK

add_bottom_timeline(slide24, 23)

# Save presentation
output_path = "c:/Users/67sdn/OneDrive/Desktop/Project/agrioptima/AgriOptima_Project_Presentation.pptx"
prs.save(output_path)
print(f"Presentation successfully generated and saved to: {output_path}")
