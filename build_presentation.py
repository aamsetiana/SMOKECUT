"""Generates the official 10-slide PPTX proposal for AIRIMPACT 2026.

Design: Modern Minimalist LIGHT — white/off-white background, dark text,
vibrant accent colors. Premium consulting-deck aesthetic.

Rules:
- Format: .pptx, 16:9 (13.333" x 7.5"), exactly 10 slides
- Fonts: Arial only, body >=18pt, refs >=12pt, headings 24-36pt+
- NO accent/stripe lines under titles or spanning edges
- NO text-only slides — every slide has a visual element
- Layouts vary per slide
- Python 3.9 compatible
"""

from __future__ import annotations
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = "AIRIMPACT2026_SMOKECUT_Proposal.pptx"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

# ── Light Palette ─────────────────────────────────────────
BG       = RGBColor(255, 255, 255)   # Pure white
BG_ALT   = RGBColor(248, 250, 252)   # #F8FAFC off-white panel
SLATE50  = RGBColor(241, 245, 249)   # #F1F5F9 card fill
BORDER   = RGBColor(203, 213, 225)   # #CBD5E1 light divider
TEXT     = RGBColor(15,  23,  42)    # #0F172A near-black
MUTED    = RGBColor(100, 116, 139)   # #64748B slate-500 body muted
WHITE    = RGBColor(255, 255, 255)

# Vibrant accents (keep on white bg for pop)
BLUE     = RGBColor(14,  165, 233)   # #0EA5E9 sky blue — primary
BLUE_D   = RGBColor(2,   132, 199)   # #0284C7 dark sky — headers
AMBER    = RGBColor(245, 158, 11)    # #F59E0B warm amber
AMBER_D  = RGBColor(180, 115, 0)     # darker amber for text on light
ROSE     = RGBColor(239, 68,  68)    # #EF4444 danger
ROSE_D   = RGBColor(185, 28,  28)    # darker rose
EMERALD  = RGBColor(5,   150, 105)   # #059669 success
EMERALD_D= RGBColor(4,   120, 87)    # darker emerald
INDIGO   = RGBColor(99,  102, 241)   # #6366F1 extra

# Cover / section accent (rich navy for contrast on white)
NAVY     = RGBColor(15,  23,  42)    # #0F172A deep navy
NAVY_MED = RGBColor(30,  58,  138)   # #1E3A8A navy-800

# Accent fill versions (very light tints for panel fills)
BLUE_TINT   = RGBColor(224, 242, 254)  # #E0F2FE
AMBER_TINT  = RGBColor(254, 243, 199)  # #FEF3C7
ROSE_TINT   = RGBColor(254, 226, 226)  # #FEE2E2
EMERALD_TINT= RGBColor(209, 250, 229)  # #D1FAE5

FONT = "Arial"


# ═══════════════════════════════════════════════════════════
# LOW-LEVEL HELPERS
# ═══════════════════════════════════════════════════════════

def bg(slide, fill=BG):
    r = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    r.line.fill.background()


def txt(slide, text, left, top, width, height,
        size=18, bold=False, color=TEXT,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name  = FONT
    p.font.size  = Pt(size)
    p.font.bold  = bold
    p.font.color.rgb = color
    p.font.italic = italic
    return tb, tf


def multiline(slide, lines, left, top, width, height, default_size=18,
              default_color=TEXT, leading=Pt(5)):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text        = item[0]
        p.font.name   = FONT
        p.font.size   = Pt(item[1] if len(item) > 1 else default_size)
        p.font.bold   = item[2] if len(item) > 2 else False
        p.font.color.rgb = item[3] if len(item) > 3 else default_color
        p.alignment   = item[4] if len(item) > 4 else PP_ALIGN.LEFT
        p.space_after = leading


def rect(slide, left, top, width, height, fill=SLATE50, border=None, bw=Pt(0)):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border; r.line.width = bw
    else:
        r.line.fill.background()
    return r


def rrect(slide, left, top, width, height, fill=SLATE50, border=None, bw=Pt(1.5)):
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border; r.line.width = bw
    else:
        r.line.fill.background()
    return r


def circle(slide, cx, cy, diameter, fill):
    r = diameter / 2
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx - r, cy - r, diameter, diameter)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.fill.background()
    return s


def circle_label(slide, cx, cy, diameter, fill, label_text,
                 label_size=26, label_color=WHITE, bold=True):
    circle(slide, cx, cy, diameter, fill)
    r = diameter / 2
    txt(slide, label_text, cx - r, cy - r, diameter, diameter,
        size=label_size, bold=bold, color=label_color,
        align=PP_ALIGN.CENTER)


def divider(slide, left, top, width, color=BORDER, thickness=0.012):
    r = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Inches(thickness))
    r.fill.solid(); r.fill.fore_color.rgb = color
    r.line.fill.background()


def tag(slide, label, left, top):
    txt(slide, label.upper(), left, top, Inches(10), Inches(0.35),
        size=11, bold=True, color=BLUE)


def slide_title(slide, title_text, left=Inches(0.75), top=Inches(0.52),
                width=Inches(11.8), size=27, color=NAVY):
    txt(slide, title_text, left, top, width, Inches(0.9),
        size=size, bold=True, color=color)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def stat_callout(slide, left, top, number, label, color=BLUE,
                 num_size=58, label_size=14):
    txt(slide, number, left, top, Inches(2.8), Inches(1.1),
        size=num_size, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(slide, label, left, top + Inches(1.05), Inches(2.8), Inches(0.6),
        size=label_size, color=MUTED, align=PP_ALIGN.CENTER)


def pill(slide, label, left, top, width=Inches(2.6),
         fill=SLATE50, border=BLUE, text_color=NAVY, size=14):
    rrect(slide, left, top, width, Inches(0.42), fill=fill, border=border, bw=Pt(1))
    txt(slide, label, left, top + Inches(0.03), width, Inches(0.4),
        size=size, color=text_color, align=PP_ALIGN.CENTER)


def tinted_panel(slide, left, top, width, height, tint, border_color):
    """Light-tinted rounded panel with vivid border."""
    rrect(slide, left, top, width, height, fill=tint, border=border_color, bw=Pt(2))


# ═══════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# Rich navy header band top + white body below
# ═══════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank)
bg(s1)

# Navy top band (~42% of slide)
rect(s1, 0, 0, prs.slide_width, Inches(3.3), fill=NAVY)

# Decorative circle motifs (inside band, right side)
circle(s1, Inches(12.4), Inches(-0.3), Inches(4.2), RGBColor(30, 58, 138))
circle(s1, Inches(12.4), Inches(-0.3), Inches(2.8), RGBColor(37, 76, 160))
circle(s1, Inches(12.4), Inches(-0.3), Inches(1.4), BLUE)

# SMOKECUT wordmark
txt(s1, "SMOKECUT",
    Inches(0.75), Inches(0.55), Inches(9.5), Inches(1.5),
    size=68, bold=True, color=WHITE)

# Tagline in band
txt(s1,
    "Software Computer Vision Berbasis Drone Standar\n"
    "untuk Pemetaan Sekat Bakar Preventif & Pencegahan Asap PM2.5",
    Inches(0.75), Inches(2.0), Inches(9.0), Inches(1.1),
    size=19, color=RGBColor(186, 230, 253), italic=True)  # blue-200

# Thin accent line separating band from white body
rect(s1, 0, Inches(3.3), prs.slide_width, Inches(0.055), fill=BLUE)

# White body — team card + event badge
txt(s1, "Tim SMOKECUT  •  AIRIMPACT 2026",
    Inches(0.75), Inches(3.55), Inches(7.0), Inches(0.5),
    size=16, bold=True, color=NAVY)
txt(s1, "@Aam  ·  @Apliy  ·  @Indra",
    Inches(0.75), Inches(4.1), Inches(7.0), Inches(0.42),
    size=15, color=MUTED)
txt(s1, "Kompetisi Solusi Kualitas Udara — MarkPlus, Inc.",
    Inches(0.75), Inches(4.55), Inches(7.0), Inches(0.42),
    size=14, color=MUTED)

# 3 highlight pills at bottom
pills_data = [
    ("🤖  Computer Vision",   BLUE_TINT,   BLUE),
    ("🌿  Drone RGB Standar", EMERALD_TINT, EMERALD),
    ("📢  WhatsApp Alert",    AMBER_TINT,   AMBER),
]
for i, (label, tint, border) in enumerate(pills_data):
    pill(s1, label, Inches(0.75) + i * Inches(3.2), Inches(5.95),
         width=Inches(2.9), fill=tint, border=border, text_color=NAVY, size=14)

# Event year badge — right side
rect(s1, Inches(10.5), Inches(3.5), Inches(2.1), Inches(2.6), fill=BLUE_TINT)
txt(s1, "2026",
    Inches(10.5), Inches(3.65), Inches(2.1), Inches(1.1),
    size=52, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
txt(s1, "AIRIMPACT",
    Inches(10.5), Inches(4.75), Inches(2.1), Inches(0.42),
    size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
txt(s1, "MarkPlus, Inc.",
    Inches(10.5), Inches(5.17), Inches(2.1), Inches(0.35),
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

notes(s1,
    "Slide pembuka. Perkenalkan nama tim, tiga anggota, dan misi utama: "
    "SMOKECUT mengubah drone RGB biasa menjadi sistem intelijen pencegahan kebakaran lahan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 2 — EXECUTIVE SUMMARY
# 3 tinted stat panels + 2-col text
# ═══════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank)
bg(s2)

tag(s2, "Executive Summary", Inches(0.75), Inches(0.28))
slide_title(s2, "Satu Platform, Tiga Lapis Perlindungan Udara")
divider(s2, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

# 3 stat panels (tinted)
stats = [
    ("≥50%", "Penurunan luas\nlahan terbakar",         BLUE,    BLUE_TINT),
    ("100%", "Gratis untuk\ndesa & MPA",               EMERALD, EMERALD_TINT),
    ("0 Rp", "Biaya sensor\nthermal tambahan",          AMBER,   AMBER_TINT),
]
panel_w = Inches(3.5)
panel_gap = Inches(0.3)
panel_start = Inches(0.75)

for i, (num, label, color, tint) in enumerate(stats):
    lx = panel_start + i * (panel_w + panel_gap)
    tinted_panel(s2, lx, Inches(1.65), panel_w, Inches(1.9), tint, color)
    txt(s2, num,
        lx, Inches(1.72), panel_w, Inches(1.0),
        size=52, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(s2, label,
        lx, Inches(2.72), panel_w, Inches(0.72),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)

divider(s2, Inches(0.75), Inches(3.68), Inches(11.8), color=BORDER)

# 2-col text
multiline(s2, [
    ("🔥  MASALAH",          13, True, ROSE),
    ("Karhutla Sumatera & Kalimantan melepaskan asap PM2.5 yang\n"
     "meracuni jutaan warga. Respons masih reaktif — pemadaman\nsetelah api meluas.",
     17, False, MUTED),
], Inches(0.75), Inches(3.82), Inches(5.5), Inches(2.8))

multiline(s2, [
    ("✅  SOLUSI SMOKECUT",   13, True, EMERALD),
    ("Analisis citra drone RGB secara lokal/offline: deteksi asap\n"
     "dini (YOLO), pemetaan semak kering (VARI), dan jalur sekat\nbakar optimal (wind-aware).",
     17, False, MUTED),
], Inches(6.9), Inches(3.82), Inches(5.65), Inches(2.8))

rect(s2, Inches(6.5), Inches(3.82), Inches(0.012), Inches(2.5), fill=BORDER)

notes(s2,
    "Tiga angka utama: 50% reduksi kebakaran, 100% gratis untuk komunitas, nol biaya hardware tambahan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM IDENTIFICATION
# 3 icon-circle rows on white, tinted left accent strip
# ═══════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank)
bg(s3)

tag(s3, "01. Problem Identification", Inches(0.75), Inches(0.28))
slide_title(s3, "Tiga Krisis yang Terabaikan di Lahan Gambut Indonesia")
divider(s3, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

problems = [
    (ROSE,    ROSE_TINT,    "🔥",
     "Kebakaran Lahan Masif & Berulang",
     "Setiap musim kemarau, Sumatera & Kalimantan kehilangan ratusan ribu hektare lahan gambut. "
     "Pola 'biarkan terbakar lalu padamkan' terus berulang tanpa sistem deteksi dini terjangkau."),
    (AMBER,   AMBER_TINT,   "🌫",
     "Paparan PM2.5 Kronik Jutaan Warga",
     "ISPU Kalimantan mencatat 3× lipat ambang batas WHO pada puncak musim asap 2023. "
     "Klaim BPJS penyakit paru melonjak 40% di provinsi terdampak (RCCC UI, 2023)."),
    (BLUE,    BLUE_TINT,    "🛠",
     "Kesenjangan Teknologi di Garis Depan",
     "Tim MPA bekerja tanpa peta bahan bakar real-time. Perencanaan sekat bakar dilakukan "
     "secara manual dan sering menempatkan relawan di zona berbahaya."),
]

row_tops = [Inches(1.72), Inches(3.12), Inches(4.52)]
for i, (color, tint, icon, title, body) in enumerate(problems):
    top = row_tops[i]
    # Tinted icon circle
    circle_label(s3, Inches(1.4), top + Inches(0.42), Inches(0.78), color, icon, 24, WHITE)
    # Title
    txt(s3, title,  Inches(2.05), top,            Inches(10.0), Inches(0.5),
        size=19, bold=True, color=NAVY)
    # Body
    txt(s3, body,   Inches(2.05), top + Inches(0.5), Inches(10.0), Inches(0.75),
        size=16, color=MUTED)
    if i < 2:
        divider(s3, Inches(2.05), top + Inches(1.3), Inches(10.0), BORDER)

notes(s3,
    "Tiga krisis saling terkait: kebakaran → asap PM2.5 → eksposur kronik warga. "
    "Akar masalahnya bukan kurangnya niat, melainkan ketiadaan alat yang terjangkau.")


# ═══════════════════════════════════════════════════════════
# SLIDE 4 — ROOT CAUSE ANALYSIS
# Split: left numbered panels | right impact list
# ═══════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank)
bg(s4)

tag(s4, "01. Problem Analysis", Inches(0.75), Inches(0.28))
slide_title(s4, "Mengapa Respons Kebakaran Selalu Terlambat?")
divider(s4, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

txt(s4, "AKAR MASALAH", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.4),
    size=12, bold=True, color=ROSE)

root_causes = [
    ("1", "Tidak ada peta bahan bakar real-time",
     "Tim MPA bekerja buta — tanpa informasi mana zona semak kering & mana yang masih lembap."),
    ("2", "Sensor thermal terlalu mahal",
     "Harga drone thermal mulai Rp 80 juta. Jauh di atas anggaran desa & komunitas MPA."),
    ("3", "Perencanaan jalur manual = tidak akurat",
     "Kalkulasi 'intuisi' tanpa mempertimbangkan arah angin & koneksi hambatan alami."),
]

for j, (num, title, body) in enumerate(root_causes):
    top = Inches(2.08) + j * Inches(1.5)
    tinted_panel(s4, Inches(0.75), top, Inches(5.65), Inches(1.3), ROSE_TINT, ROSE)
    circle_label(s4, Inches(1.3), top + Inches(0.42), Inches(0.6), ROSE, num, 20, WHITE)
    txt(s4, title, Inches(2.0), top + Inches(0.05), Inches(4.2), Inches(0.48),
        size=17, bold=True, color=NAVY)
    txt(s4, body,  Inches(2.0), top + Inches(0.52), Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

rect(s4, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=BORDER)
txt(s4, "DAMPAK NYATA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.4),
    size=12, bold=True, color=AMBER)

impacts = [
    ("📉", "Reaksi lebih lambat 4–8 jam vs deteksi awal berbasis citra"),
    ("🏥", "Biaya kesehatan PM2.5 nasional tembus Rp 1,9 triliun/tahun"),
    ("🌿", "100.000+ ha lahan gambut hangus per tahun rata-rata 2020–2024"),
    ("📡", "0% desa terdampak memiliki sistem monitoring lokal berbasis data"),
    ("🧯", "MPA sering babat jalur di arah yang justru mempercepat rambat api"),
]

for k, (ico, body) in enumerate(impacts):
    top = Inches(2.08) + k * Inches(0.98)
    circle(s4, Inches(7.3), top + Inches(0.3), Inches(0.42), AMBER_TINT)
    txt(s4, ico,  Inches(7.1),  top + Inches(0.1),  Inches(0.5),  Inches(0.45), size=18)
    txt(s4, body, Inches(7.65), top + Inches(0.05), Inches(5.5),  Inches(0.55),
        size=16, color=MUTED)

notes(s4,
    "Tiga akar masalah teknis → lima dampak terukur. Masalahnya bukan semangat relawan, "
    "tapi ketiadaan sistem berbasis data.")


# ═══════════════════════════════════════════════════════════
# SLIDE 5 — PROPOSED SOLUTION (AI ENGINE)
# Left 3-step pipeline | Right dashboard image
# ═══════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank)
bg(s5)

tag(s5, "02. Proposed Solution", Inches(0.75), Inches(0.28))
slide_title(s5, "SEKAT-AI: Tiga Lapis Analisis Computer Vision")
divider(s5, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

steps = [
    (BLUE,    BLUE_TINT,    "01", "Deteksi Asap & Titik Api Dini",
     "Model YOLOv8n ringan mendeteksi kepulan asap mikro dan heat-spot\npada frame video udara — akurat tanpa sensor thermal."),
    (AMBER,   AMBER_TINT,   "02", "Pemetaan Semak Kering via VARI",
     "Formula VARI = (G−R)/(G+R−B) mengklasifikasikan piksel ke\nzona merah (kering) dan zona hijau (aman) secara otomatis."),
    (EMERALD, EMERALD_TINT, "03", "Jalur Sekat Bakar Optimal",
     "Algoritma wind-aware menetapkan rute potong terpendek dengan\nsafety buffer ≥25 m & koneksi hambatan alami."),
]

for i, (color, tint, num, title, body) in enumerate(steps):
    top = Inches(1.72) + i * Inches(1.68)
    tinted_panel(s5, Inches(0.75), top, Inches(6.3), Inches(1.48), tint, color)
    circle_label(s5, Inches(1.3), top + Inches(0.5), Inches(0.7), color, num, 16, WHITE, True)
    txt(s5, title, Inches(2.05), top + Inches(0.1), Inches(4.8), Inches(0.5),
        size=18, bold=True, color=NAVY)
    txt(s5, body,  Inches(2.05), top + Inches(0.6), Inches(4.8), Inches(0.8),
        size=15, color=MUTED)

# Dashboard image — right half
img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "dashboard_mockup.png")
if os.path.exists(img_path):
    s5.shapes.add_picture(img_path, Inches(7.35), Inches(1.62), Inches(5.6), Inches(5.2))
else:
    tinted_panel(s5, Inches(7.35), Inches(1.62), Inches(5.6), Inches(5.2), BLUE_TINT, BLUE)
    txt(s5, "[ Dashboard Preview ]",
        Inches(7.35), Inches(3.8), Inches(5.6), Inches(0.6),
        size=18, color=MUTED, align=PP_ALIGN.CENTER)

# VARI formula strip
rrect(s5, Inches(7.35), Inches(6.52), Inches(5.6), Inches(0.42),
      fill=BLUE_TINT, border=BLUE, bw=Pt(1))
txt(s5, "VARI = (G − R) / (G + R − B)",
    Inches(7.45), Inches(6.56), Inches(5.4), Inches(0.35),
    size=13, bold=True, color=BLUE_D, align=PP_ALIGN.CENTER)

notes(s5,
    "Tiga lapis CV bekerja secara pipeline: (1) YOLO mendeteksi asap → "
    "(2) VARI memetakan bahan bakar → (3) Algoritma sekat bakar menentukan rute taktis.")


# ═══════════════════════════════════════════════════════════
# SLIDE 6 — FIELD EXECUTION
# 4 tinted step cards + tech pills
# ═══════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank)
bg(s6)

tag(s6, "03. Field Execution", Inches(0.75), Inches(0.28))
slide_title(s6, "Alur Kerja Lapangan Tim MPA — 4 Langkah Sistematis")
divider(s6, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

cols = [
    (BLUE,    BLUE_TINT,    "01", "TERBANG\n& REKAM",
     "Drone RGB standar terbang 60–100 m. File video/foto dikirim ke laptop via USB/WiFi."),
    (AMBER,   AMBER_TINT,   "02", "UNGGAH\n& PROSES",
     "SEKAT-AI Engine menganalisis: deteksi asap, heatmap VARI, rute sekat <2 menit."),
    (EMERALD, EMERALD_TINT, "03", "BABAT\nSEKAT",
     "Peta GPS dikirim ke HP MPA via WhatsApp. Tim babat jalur berdasarkan peta akurat."),
    (ROSE,    ROSE_TINT,    "04", "ALERT\nWARGA",
     "Notifikasi otomatis ke warga downwind: estimasi PM2.5, arah asap, zona evakuasi."),
]

col_w   = Inches(2.8)
col_gap = Inches(0.35)

for i, (color, tint, num, title, body) in enumerate(cols):
    lft = Inches(0.75) + i * (col_w + col_gap)
    tinted_panel(s6, lft, Inches(1.72), col_w, Inches(4.5), tint, color)
    # Large number circle
    circle_label(s6, lft + col_w / 2, Inches(2.42), Inches(1.05), color, num, 26, WHITE)
    txt(s6, title,
        lft, Inches(3.1), col_w, Inches(0.75),
        size=17, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    txt(s6, body,
        lft + Inches(0.1), Inches(3.95), col_w - Inches(0.2), Inches(2.0),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)
    # Arrow connector
    if i < 3:
        ax = lft + col_w + col_gap * 0.5 - Inches(0.1)
        txt(s6, "→", ax, Inches(2.2), Inches(0.25), Inches(0.5),
            size=20, color=BORDER, align=PP_ALIGN.CENTER)

# Tech tag pills
tech_tags = ["FastAPI + Uvicorn", "YOLOv8n", "OpenCV / VARI", "WhatsApp Gateway"]
for i, t in enumerate(tech_tags):
    pill(s6, t, Inches(0.75) + i * Inches(3.17), Inches(6.55),
         width=Inches(2.7), fill=SLATE50, border=BORDER, text_color=MUTED, size=13)

notes(s6,
    "4 langkah operasional yang bisa dijalankan relawan non-teknis. "
    "Tidak diperlukan pelatihan khusus — antarmuka dibuat semudah mungkin.")


# ═══════════════════════════════════════════════════════════
# SLIDE 7 — IMPLEMENTATION TIMELINE
# Horizontal milestone line + partner badges
# ═══════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank)
bg(s7)

tag(s7, "04. Implementation Plan", Inches(0.75), Inches(0.28))
slide_title(s7, "Peta Jalan Implementasi — 6 Bulan Pilot")
divider(s7, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

milestones = [
    (BLUE,    BLUE_TINT,    "Bulan 1–2", "Setup & Pelatihan",
     "Instalasi sistem di 2 desa pilot, kalibrasi model YOLO, pelatihan MPA operasi drone."),
    (AMBER,   AMBER_TINT,   "Bulan 3",   "Pilot Pemetaan",
     "Flight perdana, generate peta VARI & rute sekat bakar pertama, uji dispatch WA."),
    (EMERALD, EMERALD_TINT, "Bulan 4–5", "Implementasi Sekat",
     "MPA babat sekat berdasarkan peta digital. Monitor PM2.5 sebelum/sesudah."),
    (ROSE,    ROSE_TINT,    "Bulan 6",   "Evaluasi & Replikasi",
     "Laporan dampak terukur, penyempurnaan model, dokumentasi untuk replikasi 10 desa."),
]

# Spine
line_y = Inches(3.15)
rect(s7, Inches(0.75), line_y - Inches(0.012), Inches(11.8), Inches(0.025), fill=BORDER)
dot_xs = [Inches(1.6), Inches(4.6), Inches(7.6), Inches(10.6)]

for i, (color, tint, period, phase, body) in enumerate(milestones):
    x = dot_xs[i]
    # Dot
    circle(s7, x, line_y, Inches(0.3), color)
    # Content above/below alternating
    if i % 2 == 0:
        tinted_panel(s7, x - Inches(1.3), Inches(1.68), Inches(2.6), Inches(1.35), tint, color)
        txt(s7, period, x - Inches(1.3), Inches(1.73), Inches(2.6), Inches(0.38),
            size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(2.08), Inches(2.6), Inches(0.42),
            size=17, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(2.52), Inches(2.6), Inches(0.5),
            size=13, color=MUTED, align=PP_ALIGN.CENTER)
    else:
        tinted_panel(s7, x - Inches(1.3), Inches(3.42), Inches(2.6), Inches(1.35), tint, color)
        txt(s7, period, x - Inches(1.3), Inches(3.47), Inches(2.6), Inches(0.38),
            size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(3.82), Inches(2.6), Inches(0.42),
            size=17, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(4.26), Inches(2.6), Inches(0.5),
            size=13, color=MUTED, align=PP_ALIGN.CENTER)

divider(s7, Inches(0.75), Inches(5.75), Inches(11.8), color=BORDER)
txt(s7, "MITRA KUNCI", Inches(0.75), Inches(5.88), Inches(2.0), Inches(0.35),
    size=11, bold=True, color=MUTED)
partners = ["Dinas Kehutanan", "BPBD Setempat", "Dana Desa", "CSR Perkebunan"]
for i, p in enumerate(partners):
    pill(s7, p, Inches(2.95) + i * Inches(2.65), Inches(5.88),
         width=Inches(2.3), fill=SLATE50, border=BORDER, text_color=MUTED, size=13)

notes(s7,
    "6 bulan pilot dengan 4 fase. Bulan 6 bukan akhir, tapi starting point replikasi ke 10 desa lainnya.")


# ═══════════════════════════════════════════════════════════
# SLIDE 8 — RESOURCES & RISK MITIGATION
# 2-col tinted panels (green left, red right)
# ═══════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank)
bg(s8)

tag(s8, "04. Resources & Risk", Inches(0.75), Inches(0.28))
slide_title(s8, "Anggaran Efisien & Mitigasi Risiko Terstruktur")
divider(s8, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

txt(s8, "KEBUTUHAN SUMBER DAYA", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.4),
    size=12, bold=True, color=EMERALD)

resources = [
    ("💻", "Laptop Lapangan (RAM ≥8 GB)",
     "Spesifikasi standar yang sudah dimiliki sebagian besar tim MPA & dinas kehutanan."),
    ("🚁", "Drone Kamera RGB (≥1080p)",
     "Contoh: DJI Mini 2 (Rp 5–7 juta). Tidak diperlukan sensor thermal tambahan."),
    ("📶", "Koneksi Internet (Opsional)",
     "Offline-first. Internet hanya diperlukan untuk pengiriman alert WhatsApp."),
]

for j, (ico, title, body) in enumerate(resources):
    top = Inches(2.1) + j * Inches(1.5)
    tinted_panel(s8, Inches(0.75), top, Inches(5.65), Inches(1.3), EMERALD_TINT, EMERALD)
    circle_label(s8, Inches(1.3), top + Inches(0.42), Inches(0.6), EMERALD, ico, 16, WHITE)
    txt(s8, title, Inches(2.0), top + Inches(0.05), Inches(4.2), Inches(0.48),
        size=17, bold=True, color=NAVY)
    txt(s8, body,  Inches(2.0), top + Inches(0.52), Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

rect(s8, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=BORDER)
txt(s8, "MITIGASI RISIKO UTAMA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.4),
    size=12, bold=True, color=ROSE)

risks = [
    ("1", "Blank Spot Sinyal Internet",
     "SEKAT-AI berjalan penuh offline. Alert WA diantrikan dan dikirim saat sinyal tersedia."),
    ("2", "Keselamatan Tim MPA",
     "Algoritma mengunci safety buffer minimum 25–35 m dari zona api aktif secara otomatis."),
    ("3", "False Positive Deteksi",
     "Human-in-the-loop: setiap alert memerlukan konfirmasi 1 klik dari koordinator lapangan."),
]

for k, (num, title, body) in enumerate(risks):
    top = Inches(2.1) + k * Inches(1.5)
    tinted_panel(s8, Inches(6.85), top, Inches(5.65), Inches(1.3), ROSE_TINT, ROSE)
    circle_label(s8, Inches(7.4), top + Inches(0.42), Inches(0.6), ROSE, num, 20, WHITE)
    txt(s8, title, Inches(8.1), top + Inches(0.05), Inches(4.2), Inches(0.48),
        size=17, bold=True, color=NAVY)
    txt(s8, body,  Inches(8.1), top + Inches(0.52), Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

notes(s8,
    "Anggaran SMOKECUT sangat lean: tidak ada pembelian drone thermal baru. "
    "Tiga risiko utama telah dimitigasi secara teknis.")


# ═══════════════════════════════════════════════════════════
# SLIDE 9 — IMPACT & SUSTAINABILITY
# Large stat callouts in tinted panels + sustainability pills
# ═══════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank)
bg(s9)

tag(s9, "06. Expected Impact & Sustainability", Inches(0.75), Inches(0.28))
slide_title(s9, "Dampak Terukur & Model Keberlanjutan Jangka Panjang")
divider(s9, Inches(0.75), Inches(1.52), Inches(11.8), color=BORDER)

impact_stats = [
    ("≥50%", "Penurunan luas lahan\nterbakar dalam 6 bulan pilot", BLUE,    BLUE_TINT),
    ("≥80%", "Pembabatan sekat preventif\nberbasis data peta VARI",  EMERALD, EMERALD_TINT),
    ("100%", "Biomassa dikonversi jadi\nkompos / pakan ternak",       AMBER,   AMBER_TINT),
]

for i, (num, label, color, tint) in enumerate(impact_stats):
    lx = Inches(0.75) + i * (Inches(3.75) + Inches(0.2))
    tinted_panel(s9, lx, Inches(1.65), Inches(3.75), Inches(2.1), tint, color)
    txt(s9, num,   lx, Inches(1.72), Inches(3.75), Inches(1.1),
        size=60, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(s9, label, lx, Inches(2.82), Inches(3.75), Inches(0.75),
        size=14, color=MUTED, align=PP_ALIGN.CENTER)

divider(s9, Inches(0.75), Inches(3.9), Inches(11.8), color=BORDER)
txt(s9, "OUTPUT TERUKUR (PILOT 6 BULAN)", Inches(0.75), Inches(4.05),
    Inches(11.8), Inches(0.4), size=12, bold=True, color=MUTED)
txt(s9,
    "• 2 desa terpetakan penuh dengan peta semak kering per musim kemarau\n"
    "• ≥20 anggota MPA tersertifikasi operasi drone & interpretasi peta digital\n"
    "• Jalur sekat bakar terbangun di 100% zona semak merah teridentifikasi",
    Inches(0.75), Inches(4.5), Inches(11.8), Inches(0.9),
    size=17, color=MUTED)

divider(s9, Inches(0.75), Inches(5.52), Inches(11.8), color=BORDER)
txt(s9, "MODEL KEBERLANJUTAN  —  CROSS-SUBSIDY", Inches(0.75), Inches(5.65),
    Inches(6.0), Inches(0.4), size=12, bold=True, color=MUTED)

tinted_panel(s9, Inches(0.75), Inches(6.1), Inches(4.5), Inches(0.9),
             EMERALD_TINT, EMERALD)
txt(s9, "🌿  GRATIS — Desa & MPA",
    Inches(0.75), Inches(6.14), Inches(4.5), Inches(0.42),
    size=15, bold=True, color=EMERALD, align=PP_ALIGN.CENTER)
txt(s9, "Didanai Dana Desa Tanggap Bencana",
    Inches(0.75), Inches(6.56), Inches(4.5), Inches(0.35),
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

tinted_panel(s9, Inches(5.6), Inches(6.1), Inches(4.8), Inches(0.9),
             AMBER_TINT, AMBER)
txt(s9, "💼  BERBAYAR — Korporasi & Dinas",
    Inches(5.6), Inches(6.14), Inches(4.8), Inches(0.42),
    size=15, bold=True, color=AMBER_D, align=PP_ALIGN.CENTER)
txt(s9, "CSR Perkebunan & Dinas Lingkungan Hidup",
    Inches(5.6), Inches(6.56), Inches(4.8), Inches(0.35),
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

notes(s9,
    "Impact slide: tiga angka utama memperlihatkan hasil konkret. Cross-subsidy model memastikan "
    "komunitas desa & MPA tidak dibebankan biaya apapun.")


# ═══════════════════════════════════════════════════════════
# SLIDE 10 — CONCLUSION & REFERENCES
# Navy top band mirror of cover + white references below
# ═══════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank)
bg(s10)

# Navy top band (mirrors cover)
rect(s10, 0, 0, prs.slide_width, Inches(3.6), fill=NAVY)
rect(s10, 0, Inches(3.6), prs.slide_width, Inches(0.055), fill=BLUE)

# Decorative circle motifs
circle(s10, Inches(0.5), Inches(3.9), Inches(3.8), RGBColor(241, 245, 249))
circle(s10, Inches(0.5), Inches(3.9), Inches(2.4), RGBColor(248, 250, 252))

# SMOKECUT wordmark small — top left
txt(s10, "SMOKECUT",
    Inches(0.75), Inches(0.4), Inches(4.0), Inches(0.6),
    size=16, bold=True, color=BLUE)

# Central quote in band
txt(s10,
    "\u201cKualitas udara bersih tidak dimulai saat masker dipakai —\n"
    "tetapi saat asap dicegah mengepul ke udara.\u201d",
    Inches(0.75), Inches(1.1), Inches(11.8), Inches(1.6),
    size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER, italic=True)

txt(s10, "— Tim SMOKECUT, AIRIMPACT 2026",
    Inches(0.75), Inches(2.82), Inches(11.8), Inches(0.42),
    size=15, color=RGBColor(186, 230, 253), align=PP_ALIGN.CENTER)

# References section — white body
txt(s10, "REFERENSI KUNCI", Inches(0.75), Inches(3.75), Inches(11.8), Inches(0.38),
    size=11, bold=True, color=MUTED)

refs_left = (
    "1. MarkPlus, Inc. (2025). Survei Persepsi Masyarakat terhadap Kualitas Udara "
    "(Guidebook AIRIMPACT 2026).\n"
    "2. IQAir. (2026). Jabodetabek Air Quality Snapshot, 29 Oktober 2026.\n"
    "3. RCCC UI. (2023). Kajian Klaim BPJS Kesehatan Terkait Penyakit Polusi Udara di Jakarta."
)
refs_right = (
    "4. Permen LHK No. 28 Tahun 2021 tentang Sistem Pengendalian Kebakaran Hutan dan Lahan.\n"
    "5. Gitelson, A.A., et al. (2002). Novel Algorithms for Remote Estimation of Vegetation "
    "Fraction (VARI). Remote Sensing of Environment.\n"
    "6. USDA Forest Service. (2018). Fire Management Guidelines: Fuel Breaks & Safety Zones."
)

txt(s10, refs_left,  Inches(0.75), Inches(4.2), Inches(5.8), Inches(2.5),
    size=13, color=MUTED)
txt(s10, refs_right, Inches(6.85), Inches(4.2), Inches(5.8), Inches(2.5),
    size=13, color=MUTED)
rect(s10, Inches(6.5), Inches(4.2), Inches(0.012), Inches(2.5), fill=BORDER)

txt(s10, "Terima kasih — Dewan Juri AIRIMPACT 2026",
    Inches(0.75), Inches(6.9), Inches(8.0), Inches(0.42),
    size=15, color=MUTED, italic=True)

notes(s10,
    "Tutup dengan kutipan inti SMOKECUT. Siap untuk sesi tanya jawab — "
    "tekankan: sistem sudah berjalan dan bisa didemonstrasikan langsung.")


# ═══════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════
prs.save(OUTPUT_FILE)
print(f"✅  Presentation saved → {OUTPUT_FILE}  ({len(prs.slides)} slides)")
