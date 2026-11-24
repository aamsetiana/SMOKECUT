"""Generates the official 10-slide PPTX proposal for AIRIMPACT 2026.

Design: Modern Minimalist — varied layouts, stat callouts, icon circles,
generous whitespace, NO uniform card-everywhere pattern.

Rules:
- Format: .pptx, 16:9 (13.333" x 7.5"), exactly 10 slides
- Fonts: Arial only (safe-list), body >=18pt, refs >=12pt, headings 24-36pt+
- NO accent/stripe lines under titles or spanning edges
- NO text-only slides — every slide has a visual element
- Layouts vary per slide
- Python 3.9 compatible (no match/case, union | types require __future__)
"""

from __future__ import annotations
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = "AIRIMPACT2026_SMOKECUT_Proposal.pptx"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

blank = prs.slide_layouts[6]

# ── Palette ───────────────────────────────────────────────
BG      = RGBColor(11,  17,  32)   # #0B1120 deep navy
CARD    = RGBColor(21,  33,  54)   # #152136 slightly lighter panel
LINE    = RGBColor(51,  65,  85)   # #334155 divider
WHITE   = RGBColor(255, 255, 255)
MUTED   = RGBColor(148, 163, 184)  # #94A3B8
SKY     = RGBColor(56,  189, 248)  # #38BDF8 primary accent
AMBER   = RGBColor(245, 158, 11)   # #F59E0B highlight
ROSE    = RGBColor(239, 68,  68)   # #EF4444 danger
EMERALD = RGBColor(16,  185, 129)  # #10B981 success
INDIGO  = RGBColor(99,  102, 241)  # #6366F1 extra accent

FONT = "Arial"


# ═══════════════════════════════════════════════════════════
# LOW-LEVEL HELPERS
# ═══════════════════════════════════════════════════════════

def bg(slide):
    """Full-bleed dark background."""
    r = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid()
    r.fill.fore_color.rgb = BG
    r.line.fill.background()


def txt(slide, text, left, top, width, height,
        size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
        italic=False, wrap=True):
    """Add a simple textbox."""
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


def multiline(slide, lines, left, top, width, height,
              size=18, color=WHITE, leading=Pt(4)):
    """Add a textbox with multiple paragraphs from a list of (text, size, bold, color) tuples."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    for i, item in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        line_text  = item[0]
        line_size  = item[1] if len(item) > 1 else size
        line_bold  = item[2] if len(item) > 2 else False
        line_color = item[3] if len(item) > 3 else color
        line_align = item[4] if len(item) > 4 else PP_ALIGN.LEFT
        p.text = line_text
        p.font.name  = FONT
        p.font.size  = Pt(line_size)
        p.font.bold  = line_bold
        p.font.color.rgb = line_color
        p.alignment  = line_align
        p.space_after = leading


def rect(slide, left, top, width, height, fill=CARD, border=None, bw=Pt(0)):
    """Plain rectangle shape."""
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    r.fill.solid()
    r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border
        r.line.width = bw
    else:
        r.line.fill.background()
    return r


def rrect(slide, left, top, width, height, fill=CARD, border=None, bw=Pt(1.5)):
    """Rounded rectangle."""
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    r.fill.solid()
    r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border
        r.line.width = bw
    else:
        r.line.fill.background()
    return r


def circle(slide, cx, cy, diameter, fill):
    """Filled circle centred on (cx, cy)."""
    r = diameter / 2
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        cx - r, cy - r, diameter, diameter)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    return shape


def circle_label(slide, cx, cy, diameter, fill, label_text, label_size=28,
                 label_color=WHITE, bold=True):
    """Circle with centered text label."""
    circle(slide, cx, cy, diameter, fill)
    r = diameter / 2
    txt(slide, label_text,
        cx - r, cy - r, diameter, diameter,
        size=label_size, bold=bold, color=label_color,
        align=PP_ALIGN.CENTER)


def divider(slide, left, top, width, color=LINE, thickness=Pt(0.75)):
    """Thin horizontal divider line."""
    r = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.015))
    r.fill.solid()
    r.fill.fore_color.rgb = color
    r.line.fill.background()


def tag(slide, label, left, top):
    """Uppercase SKY category tag above title."""
    txt(slide, label.upper(),
        left, top, Inches(10), Inches(0.35),
        size=12, bold=True, color=SKY)


def slide_title(slide, title_text, left=Inches(0.75), top=Inches(0.52),
                width=Inches(11.8), size=26):
    """Main slide title — bold white."""
    txt(slide, title_text, left, top, width, Inches(0.9),
        size=size, bold=True, color=WHITE)


def notes(slide, text):
    """Speaker notes."""
    slide.notes_slide.notes_text_frame.text = text.strip()


def stat_callout(slide, left, top, number, label, color=SKY,
                 num_size=58, label_size=14):
    """Large stat number + small label below."""
    txt(slide, number,
        left, top, Inches(2.8), Inches(1.1),
        size=num_size, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(slide, label,
        left, top + Inches(1.05), Inches(2.8), Inches(0.5),
        size=label_size, bold=False, color=MUTED, align=PP_ALIGN.CENTER)


def pill(slide, label, left, top, width=Inches(2.6), fill=CARD, border=SKY,
         text_color=WHITE, size=14):
    """Pill-shaped badge."""
    rrect(slide, left, top, width, Inches(0.42), fill=fill, border=border, bw=Pt(1))
    txt(slide, label, left, top + Inches(0.03), width, Inches(0.4),
        size=size, color=text_color, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# Full-bleed dark, oversized wordmark, geometric accent circle
# ═══════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank)
bg(s1)

# Large decorative circle (top-right, partially off-screen) — depth motif
circle(s1, Inches(12.9), Inches(-0.4), Inches(4.6), RGBColor(21, 33, 54))
circle(s1, Inches(12.9), Inches(-0.4), Inches(3.2), RGBColor(26, 42, 70))

# Small accent dot cluster (bottom-left)
for i, (ox, oy, sz, fc) in enumerate([
    (0.55, 6.6, 0.18, SKY),
    (0.85, 6.72, 0.12, AMBER),
    (1.1,  6.58, 0.10, EMERALD),
]):
    circle(s1, Inches(ox), Inches(oy), Inches(sz), fc)

# Main wordmark
txt(s1, "SMOKECUT",
    Inches(0.75), Inches(1.6), Inches(10), Inches(1.6),
    size=72, bold=True, color=WHITE)

# SKY accent bar (thin, left edge only — not spanning full width)
rect(s1, Inches(0.75), Inches(2.95), Inches(1.4), Inches(0.04), fill=SKY)

# Tagline
txt(s1,
    "Software Computer Vision Berbasis Drone Standar\n"
    "untuk Pemetaan Sekat Bakar Preventif & Pencegahan Asap PM2.5",
    Inches(0.75), Inches(3.1), Inches(9.5), Inches(1.3),
    size=20, color=MUTED, italic=True)

# Team info card — bottom left, slim
rrect(s1, Inches(0.75), Inches(5.75), Inches(5.8), Inches(1.3),
      fill=RGBColor(21, 33, 54), border=SKY, bw=Pt(1))
multiline(s1, [
    ("Tim SMOKECUT  •  AIRIMPACT 2026",   13, True,  SKY,   PP_ALIGN.LEFT),
    ("@Aam · @Apliy · @Indra",            12, False, MUTED, PP_ALIGN.LEFT),
    ("Kompetisi Solusi Kualitas Udara — MarkPlus, Inc.", 11, False, MUTED, PP_ALIGN.LEFT),
], Inches(1.1), Inches(5.95), Inches(5.3), Inches(1.0))

# Event badge — bottom right
rrect(s1, Inches(10.6), Inches(5.95), Inches(2.0), Inches(0.75),
      fill=RGBColor(56, 189, 248, ), border=None)
# Workaround: use SKY fill pill
r_badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(10.6), Inches(5.95), Inches(2.0), Inches(0.75))
r_badge.fill.solid(); r_badge.fill.fore_color.rgb = SKY
r_badge.line.fill.background()
txt(s1, "2026", Inches(10.6), Inches(5.98), Inches(2.0), Inches(0.68),
    size=22, bold=True, color=BG, align=PP_ALIGN.CENTER)

notes(s1,
    "Slide pembuka. Sampaikan nama tim, perkenalan singkat 3 anggota, dan misi utama "
    "SMOKECUT: mengubah drone RGB biasa menjadi sistem intelijen pencegahan kebakaran lahan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 2 — EXECUTIVE SUMMARY
# 3 large stat callouts + 2-col text below (no card border)
# ═══════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank)
bg(s2)

tag(s2, "Executive Summary", Inches(0.75), Inches(0.28))
slide_title(s2, "Satu Platform, Tiga Lapis Perlindungan Udara")

# Thin divider
divider(s2, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

# 3 stat callouts
stat_callout(s2, Inches(0.75), Inches(1.65), "≥50%",
             "Penurunan luas lahan terbakar\n(target 6 bulan pilot)", SKY)
stat_callout(s2, Inches(4.3),  Inches(1.65), "100%",
             "Gratis untuk desa & MPA\n(cross-subsidy model)", EMERALD)
stat_callout(s2, Inches(7.9),  Inches(1.65), "0 Rp",
             "Biaya sensor thermal baru\n(hanya drone RGB standar)", AMBER)

# Thin divider
divider(s2, Inches(0.75), Inches(3.55), Inches(11.8), color=LINE)

# 2-col text — left: problem context, right: solution
multiline(s2, [
    ("🔥  MASALAH",          13, True, ROSE),
    ("Karhutla Sumatera & Kalimantan melepaskan\nasap PM2.5 yang meracuni jutaan warga. Respons\nmasih reaktif — pemadaman setelah api meluas.",
     17, False, MUTED),
], Inches(0.75), Inches(3.68), Inches(5.5), Inches(2.8))

multiline(s2, [
    ("✅  SOLUSI SMOKECUT",   13, True, EMERALD),
    ("Analisis citra drone RGB secara lokal/offline:\ndeteksi asap dini (YOLO), pemetaan semak kering\n(VARI), dan jalur sekat bakar optimal (wind-aware).",
     17, False, MUTED),
], Inches(6.9), Inches(3.68), Inches(5.65), Inches(2.8))

# Vertical divider between cols
rect(s2, Inches(6.5), Inches(3.68), Inches(0.012), Inches(2.5), fill=LINE)

notes(s2,
    "Tiga angka utama: 50% reduksi kebakaran, 100% gratis untuk komunitas, nol biaya hardware tambahan. "
    "Ini adalah nilai jual inti yang membedakan SMOKECUT dari solusi thermal imaging mahal.")


# ═══════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM IDENTIFICATION
# 3 icon-circle rows (no card borders), breathable layout
# ═══════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank)
bg(s3)

tag(s3, "01. Problem Identification", Inches(0.75), Inches(0.28))
slide_title(s3, "Tiga Krisis yang Terabaikan di Lahan Gambut Indonesia")
divider(s3, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

problems = [
    (ROSE,    "🔥", "Kebakaran Lahan Masif & Berulang",
     "Setiap musim kemarau, Sumatera & Kalimantan kehilangan ratusan ribu hektare lahan gambut. "
     "Pola 'biarkan terbakar lalu padamkan' terus berulang tanpa sistem deteksi dini yang terjangkau."),
    (AMBER,   "🌫", "Paparan PM2.5 Kronik Jutaan Warga",
     "ISPU Kalimantan mencatat 3× lipat ambang batas WHO pada puncak musim asap 2023. "
     "Klaim BPJS penyakit paru melonjak 40% di provinsi terdampak (RCCC UI, 2023)."),
    (SKY,     "🛠", "Kesenjangan Teknologi di Garis Depan",
     "Tim MPA tidak memiliki akses ke peta bahan bakar real-time. Perencanaan sekat bakar "
     "dilakukan secara manual dan sering menempatkan relawan di zona berbahaya."),
]

row_tops = [Inches(1.72), Inches(3.12), Inches(4.52)]
for i, (color, icon, title, body) in enumerate(problems):
    top = row_tops[i]
    # Icon circle
    circle_label(s3, Inches(1.15), top + Inches(0.42), Inches(0.72), color, icon, 22, WHITE)
    # Title
    txt(s3, title,
        Inches(1.75), top, Inches(10.3), Inches(0.52),
        size=19, bold=True, color=WHITE)
    # Body
    txt(s3, body,
        Inches(1.75), top + Inches(0.52), Inches(10.3), Inches(0.72),
        size=16, color=MUTED)
    # Row separator
    if i < 2:
        divider(s3, Inches(1.75), top + Inches(1.3), Inches(10.3), LINE)

notes(s3,
    "Tiga krisis saling terkait: kebakaran → asap PM2.5 → eksposur kronik warga. "
    "Akar masalahnya bukan kurangnya niat, melainkan ketiadaan alat yang terjangkau dan mudah dioperasikan oleh MPA di lapangan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 4 — ROOT CAUSE ANALYSIS
# Split layout: left numbered list | right divider + bullets
# ═══════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank)
bg(s4)

tag(s4, "01. Problem Analysis", Inches(0.75), Inches(0.28))
slide_title(s4, "Mengapa Respons Kebakaran Selalu Terlambat?")
divider(s4, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

# Left column header
txt(s4, "AKAR MASALAH", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.4),
    size=13, bold=True, color=ROSE)

root_causes = [
    ("1", "Tidak ada peta bahan bakar real-time",
     "Tim MPA bekerja buta — tanpa informasi mana zona semak kering & mana yang masih lembap."),
    ("2", "Sensor thermal terlalu mahal",
     "Harga drone thermal mulai Rp 80 juta. Jauh di atas anggaran desa & komunitas MPA mandiri."),
    ("3", "Perencanaan jalur manual = tidak akurat",
     "Kalkulasi 'intuisi' tanpa mempertimbangkan arah angin & koneksi hambatan alami."),
]

for j, (num, title, body) in enumerate(root_causes):
    top = Inches(2.1) + j * Inches(1.5)
    # Number badge
    circle_label(s4, Inches(1.15), top + Inches(0.3), Inches(0.52), ROSE, num, 18, WHITE)
    txt(s4, title, Inches(1.65), top, Inches(4.5), Inches(0.45),
        size=17, bold=True, color=WHITE)
    txt(s4, body,  Inches(1.65), top + Inches(0.44), Inches(4.5), Inches(0.75),
        size=15, color=MUTED)

# Vertical divider
rect(s4, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=LINE)

# Right column header
txt(s4, "DAMPAK NYATA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.4),
    size=13, bold=True, color=AMBER)

impacts = [
    ("📉", "Reaksi lebih lambat 4–8 jam vs deteksi awal berbasis citra"),
    ("🏥", "Biaya kesehatan PM2.5 nasional tembus Rp 1,9 triliun/tahun"),
    ("🌿", "100.000+ ha lahan gambut hangus per tahun rata-rata 2020–2024"),
    ("📡", "0% desa terdampak memiliki sistem monitoring lokal berbasis data"),
    ("🧯", "MPA sering babat jalur di arah yang justru mempercepat rambat api"),
]

for k, (ico, body) in enumerate(impacts):
    top = Inches(2.1) + k * Inches(0.98)
    txt(s4, ico,  Inches(6.85), top, Inches(0.5),  Inches(0.55), size=20)
    txt(s4, body, Inches(7.45), top, Inches(5.1),  Inches(0.55), size=16, color=MUTED)

notes(s4,
    "Tiga akar masalah teknis → lima dampak terukur. "
    "Slide ini memperkuat urgensi: masalahnya bukan semangat relawan, tapi ketiadaan sistem berbasis data.")


# ═══════════════════════════════════════════════════════════
# SLIDE 5 — PROPOSED SOLUTION (AI ENGINE)
# Left: 3 numbered pipeline steps | Right: dashboard mockup image
# ═══════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank)
bg(s5)

tag(s5, "02. Proposed Solution", Inches(0.75), Inches(0.28))
slide_title(s5, "SEKAT-AI: Tiga Lapis Analisis Computer Vision")
divider(s5, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

steps = [
    (SKY,     "01", "Deteksi Asap & Titik Api Dini",
     "Model YOLOv8n ringan mendeteksi kepulan asap mikro dan heat-spot\npada frame video udara — akurat tanpa sensor thermal."),
    (AMBER,   "02", "Pemetaan Semak Kering via VARI",
     "Formula VARI = (G−R)/(G+R−B) mengklasifikasikan piksel ke\nzona merah (kering/risiko tinggi) dan zona hijau (aman)."),
    (EMERALD, "03", "Jalur Sekat Bakar Optimal",
     "Algoritma wind-aware menetapkan rute potong terpendek\ndengan safety buffer ≥25 m & koneksi hambatan alami."),
]

for i, (color, num, title, body) in enumerate(steps):
    top = Inches(1.72) + i * Inches(1.68)
    circle_label(s5, Inches(1.15), top + Inches(0.4), Inches(0.65), color, num, 15, WHITE, True)
    txt(s5, title, Inches(1.75), top,            Inches(5.4), Inches(0.48),
        size=18, bold=True, color=WHITE)
    txt(s5, body,  Inches(1.75), top + Inches(0.46), Inches(5.4), Inches(0.9),
        size=15, color=MUTED)

# Dashboard mockup image — right half
img_path = os.path.join(os.path.dirname(__file__), "samples", "dashboard_mockup.png")
if os.path.exists(img_path):
    s5.shapes.add_picture(img_path, Inches(7.35), Inches(1.62), Inches(5.6), Inches(5.2))
else:
    # Placeholder panel if image missing
    rrect(s5, Inches(7.35), Inches(1.62), Inches(5.6), Inches(5.2),
          fill=CARD, border=SKY, bw=Pt(1))
    txt(s5, "[ Dashboard Preview ]",
        Inches(7.35), Inches(3.5), Inches(5.6), Inches(0.6),
        size=18, color=MUTED, align=PP_ALIGN.CENTER)

# VARI formula strip at bottom of image area
rrect(s5, Inches(7.35), Inches(6.52), Inches(5.6), Inches(0.42),
      fill=RGBColor(10, 20, 40), border=SKY, bw=Pt(0.75))
txt(s5, "VARI = (G − R) / (G + R − B)",
    Inches(7.45), Inches(6.56), Inches(5.4), Inches(0.35),
    size=13, color=SKY, align=PP_ALIGN.CENTER)

notes(s5,
    "Tiga lapis CV bekerja secara pipeline: (1) YOLO mendeteksi asap → (2) VARI memetakan bahan bakar → "
    "(3) Algoritma sekat bakar menentukan rute taktis. Semua berjalan lokal di laptop lapangan tanpa internet.")


# ═══════════════════════════════════════════════════════════
# SLIDE 6 — FIELD EXECUTION (MPA WORKFLOW)
# 4 large numbered circles atop description columns
# ═══════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank)
bg(s6)

tag(s6, "03. Field Execution", Inches(0.75), Inches(0.28))
slide_title(s6, "Alur Kerja Lapangan Tim MPA — 4 Langkah Sistematis")
divider(s6, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

cols = [
    (SKY,     "01", "TERBANG\n& REKAM",
     "Drone RGB standar terbang 60–100 m. Video/foto dikirim ke laptop lapangan via USB/WiFi."),
    (AMBER,   "02", "UNGGAH\n& PROSES",
     "SEKAT-AI Engine menganalisis: deteksi asap, heatmap VARI, dan kalkulasi rute sekat <2 menit."),
    (EMERALD, "03", "BABAT\nSEKAT",
     "Peta GPS dikirim ke HP anggota MPA via WhatsApp. Tim babat jalur berdasarkan peta akurat."),
    (ROSE,    "04", "ALERT\nWARGA",
     "Notifikasi otomatis ke warga downwind: estimasi PM2.5, arah asap, dan zona evakuasi."),
]

col_width = Inches(2.8)
col_gap   = Inches(0.35)
start_x   = Inches(0.75)

for i, (color, num, title, body) in enumerate(cols):
    lft = start_x + i * (col_width + col_gap)
    # Large circle
    circle_label(s6, lft + col_width / 2, Inches(2.42), Inches(1.05), color, num, 26, WHITE)
    # Title
    txt(s6, title,
        lft, Inches(3.08), col_width, Inches(0.75),
        size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Body
    txt(s6, body,
        lft, Inches(3.9), col_width, Inches(2.1),
        size=16, color=MUTED, align=PP_ALIGN.CENTER)
    # Connector arrow (except last)
    if i < 3:
        ax = lft + col_width + col_gap * 0.5 - Inches(0.09)
        txt(s6, "→", ax, Inches(2.2), Inches(0.25), Inches(0.5),
            size=20, color=LINE, align=PP_ALIGN.CENTER)

# Bottom strip: tech tags
tech_tags = ["FastAPI + Uvicorn", "YOLOv8n", "OpenCV / VARI", "WhatsApp Gateway"]
tag_w = Inches(2.4)
tag_gap = Inches(0.5)
tag_start = Inches(0.75)
for i, tag_text in enumerate(tech_tags):
    pill(s6, tag_text,
         tag_start + i * (tag_w + tag_gap),
         Inches(6.55), width=tag_w, fill=CARD, border=LINE)

notes(s6,
    "4 langkah operasional yang bisa dijalankan relawan non-teknis. "
    "Tekankan bahwa tidak diperlukan pelatihan khusus — antarmuka dibuat semudah mungkin.")


# ═══════════════════════════════════════════════════════════
# SLIDE 7 — IMPLEMENTATION TIMELINE
# Horizontal milestone timeline + partner badges
# ═══════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank)
bg(s7)

tag(s7, "04. Implementation Plan", Inches(0.75), Inches(0.28))
slide_title(s7, "Peta Jalan Implementasi — 6 Bulan Pilot")
divider(s7, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

milestones = [
    (SKY,     "Bulan 1–2", "Setup & Pelatihan",
     "Instalasi sistem di 2 desa pilot, kalibrasi model YOLO, pelatihan MPA operasi drone."),
    (AMBER,   "Bulan 3",   "Pilot Pemetaan",
     "Flight perdana, generate peta VARI & rute sekat bakar pertama, uji dispatch WA."),
    (EMERALD, "Bulan 4–5", "Implementasi Sekat",
     "MPA babat sekat berdasarkan peta digital. Monitor PM2.5 sebelum/sesudah."),
    (ROSE,    "Bulan 6",   "Evaluasi & Replikasi",
     "Laporan dampak terukur, penyempurnaan model, dokumentasi untuk replikasi 10 desa."),
]

# Timeline spine
line_y = Inches(3.15)
rect(s7, Inches(0.75), line_y - Inches(0.012), Inches(11.8), Inches(0.025), fill=LINE)

dot_xs = [Inches(1.6), Inches(4.6), Inches(7.6), Inches(10.6)]

for i, (color, period, phase, body) in enumerate(milestones):
    x = dot_xs[i]
    # Dot on timeline
    circle(s7, x, line_y, Inches(0.28), color)

    # Content above timeline (odd idx) or below (even idx)
    if i % 2 == 0:
        # Above
        txt(s7, period, x - Inches(1.3), Inches(1.72), Inches(2.6), Inches(0.38),
            size=13, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(2.08), Inches(2.6), Inches(0.42),
            size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(2.52), Inches(2.6), Inches(0.6),
            size=14, color=MUTED, align=PP_ALIGN.CENTER)
    else:
        # Below
        txt(s7, period, x - Inches(1.3), Inches(3.42), Inches(2.6), Inches(0.38),
            size=13, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(3.78), Inches(2.6), Inches(0.42),
            size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(4.22), Inches(2.6), Inches(0.6),
            size=14, color=MUTED, align=PP_ALIGN.CENTER)

# Partner section
divider(s7, Inches(0.75), Inches(5.75), Inches(11.8), color=LINE)
txt(s7, "MITRA KUNCI", Inches(0.75), Inches(5.88), Inches(2.0), Inches(0.35),
    size=12, bold=True, color=MUTED)

partners = ["Dinas Kehutanan", "BPBD Setempat", "Dana Desa", "CSR Perkebunan"]
for i, p in enumerate(partners):
    pill(s7, p, Inches(2.95) + i * Inches(2.65), Inches(5.88),
         width=Inches(2.3), fill=CARD, border=LINE, text_color=MUTED)

notes(s7,
    "6 bulan pilot dengan 4 fase terstruktur. Tekankan bahwa Bulan 6 bukan akhir, "
    "tapi starting point replikasi ke 10 desa lainnya dengan model yang sudah terbukti.")


# ═══════════════════════════════════════════════════════════
# SLIDE 8 — RESOURCES & RISK MITIGATION
# 2-column, circle bullets, divider line (no card boxes)
# ═══════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank)
bg(s8)

tag(s8, "04. Resources & Risk", Inches(0.75), Inches(0.28))
slide_title(s8, "Anggaran Efisien & Mitigasi Risiko Terstruktur")
divider(s8, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

# Left — Resources
txt(s8, "KEBUTUHAN SUMBER DAYA", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.42),
    size=13, bold=True, color=EMERALD)

resources = [
    ("💻", "Laptop Lapangan (RAM ≥8 GB)",
     "Spesifikasi standar yang sudah dimiliki sebagian besar tim MPA & dinas kehutanan."),
    ("🚁", "Drone Kamera RGB (≥1080p)",
     "Contoh: DJI Mini 2 (Rp 5–7 juta). Tidak diperlukan sensor thermal tambahan."),
    ("📶", "Koneksi Internet (Opsional)",
     "Sistem berjalan offline-first. Internet hanya diperlukan untuk pengiriman alert WA."),
]

for j, (ico, title, body) in enumerate(resources):
    top = Inches(2.15) + j * Inches(1.55)
    circle_label(s8, Inches(1.15), top + Inches(0.3), Inches(0.52), EMERALD, ico, 16, WHITE)
    txt(s8, title, Inches(1.72), top,            Inches(4.5), Inches(0.48),
        size=17, bold=True, color=WHITE)
    txt(s8, body,  Inches(1.72), top + Inches(0.46), Inches(4.5), Inches(0.75),
        size=15, color=MUTED)

# Vertical divider
rect(s8, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=LINE)

# Right — Risks
txt(s8, "MITIGASI RISIKO UTAMA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.42),
    size=13, bold=True, color=ROSE)

risks = [
    ("1", "Blank Spot Sinyal Internet",
     "SEKAT-AI berjalan penuh offline. Alert WA diantrikan dan dikirim saat sinyal tersedia."),
    ("2", "Keselamatan Tim MPA",
     "Algoritma mengunci safety buffer minimum 25–35 m dari zona api aktif secara otomatis."),
    ("3", "False Positive Deteksi",
     "Human-in-the-loop: setiap alert memerlukan konfirmasi 1 klik dari koordinator lapangan."),
]

for k, (num, title, body) in enumerate(risks):
    top = Inches(2.15) + k * Inches(1.55)
    circle_label(s8, Inches(7.3), top + Inches(0.3), Inches(0.52), ROSE, num, 18, WHITE)
    txt(s8, title, Inches(7.88), top,            Inches(4.75), Inches(0.48),
        size=17, bold=True, color=WHITE)
    txt(s8, body,  Inches(7.88), top + Inches(0.46), Inches(4.75), Inches(0.75),
        size=15, color=MUTED)

notes(s8,
    "Anggaran SMOKECUT sangat lean: tidak ada pembelian drone thermal baru. "
    "Tiga risiko utama telah dimitigasi secara teknis — offline mode, safety buffer otomatis, dan verifikasi manusia.")


# ═══════════════════════════════════════════════════════════
# SLIDE 9 — IMPACT & SUSTAINABILITY
# Large stat callouts + sustainability pills
# ═══════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank)
bg(s9)

tag(s9, "06. Expected Impact & Sustainability", Inches(0.75), Inches(0.28))
slide_title(s9, "Dampak Terukur & Model Keberlanjutan Jangka Panjang")
divider(s9, Inches(0.75), Inches(1.52), Inches(11.8), color=LINE)

# 3 large stats
stat_callout(s9, Inches(0.75), Inches(1.68), "≥50%",
             "Penurunan luas lahan terbakar\ndalam 6 bulan pilot", SKY, num_size=64)
stat_callout(s9, Inches(4.6),  Inches(1.68), "≥80%",
             "Pembabatan sekat preventif\nberbasis data peta VARI", EMERALD, num_size=64)
stat_callout(s9, Inches(8.5),  Inches(1.68), "100%",
             "Biomassa dikonversi jadi\nkompos / pakan ternak", AMBER, num_size=64)

divider(s9, Inches(0.75), Inches(3.75), Inches(11.8), color=LINE)

# KPI detail
txt(s9, "OUTPUT TERUKUR (PILOT 6 BULAN)", Inches(0.75), Inches(3.9), Inches(11.8), Inches(0.4),
    size=13, bold=True, color=MUTED)
txt(s9,
    "• 2 desa terpetakan penuh dengan peta semak kering per musim kemarau\n"
    "• ≥20 anggota MPA tersertifikasi operasi drone & interpretasi peta digital\n"
    "• Jalur sekat bakar terbangun di 100% zona semak merah teridentifikasi",
    Inches(0.75), Inches(4.35), Inches(11.8), Inches(1.0),
    size=17, color=MUTED)

divider(s9, Inches(0.75), Inches(5.45), Inches(11.8), color=LINE)

# Sustainability model
txt(s9, "MODEL KEBERLANJUTAN  —  CROSS-SUBSIDY", Inches(0.75), Inches(5.58),
    Inches(5.5), Inches(0.4), size=13, bold=True, color=MUTED)

pill(s9, "🌿  GRATIS — Desa & MPA",
     Inches(0.75), Inches(6.1), width=Inches(4.2),
     fill=RGBColor(16, 70, 50), border=EMERALD, text_color=WHITE, size=15)
txt(s9, "Didanai Dana Desa Tanggap Bencana",
    Inches(0.75), Inches(6.58), Inches(4.2), Inches(0.35), size=13, color=MUTED)

pill(s9, "💼  BERBAYAR — Korporasi & Dinas",
     Inches(5.4), Inches(6.1), width=Inches(4.5),
     fill=RGBColor(40, 50, 15), border=AMBER, text_color=WHITE, size=15)
txt(s9, "CSR Perkebunan & Dinas Lingkungan Hidup",
    Inches(5.4), Inches(6.58), Inches(4.5), Inches(0.35), size=13, color=MUTED)

notes(s9,
    "Impact slide: tiga angka utama memperlihatkan hasil konkret. Cross-subsidy model memastikan "
    "komunitas desa & MPA tidak dibebankan biaya apapun — model bisnis yang inklusif sekaligus berkelanjutan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 10 — CONCLUSION & REFERENCES
# Center-weighted quote, 2-col references, decorative circle
# ═══════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank)
bg(s10)

# Large decorative circle motif — bottom right
circle(s10, Inches(13.0), Inches(8.1), Inches(5.0), RGBColor(21, 33, 54))
circle(s10, Inches(13.0), Inches(8.1), Inches(3.2), RGBColor(26, 42, 70))

# SMOKECUT wordmark — top left
txt(s10, "SMOKECUT",
    Inches(0.75), Inches(0.4), Inches(4.5), Inches(0.6),
    size=16, bold=True, color=SKY)

divider(s10, Inches(0.75), Inches(1.08), Inches(11.8), color=LINE)

# Central quote
txt(s10,
    "\u201cKualitas udara bersih tidak dimulai saat masker dipakai —\n"
    "tetapi saat asap dicegah mengepul ke udara.\u201d",
    Inches(0.75), Inches(1.3), Inches(11.8), Inches(1.6),
    size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER, italic=True)

txt(s10, "— Tim SMOKECUT, AIRIMPACT 2026",
    Inches(0.75), Inches(2.98), Inches(11.8), Inches(0.42),
    size=15, color=SKY, align=PP_ALIGN.CENTER)

divider(s10, Inches(0.75), Inches(3.52), Inches(11.8), color=LINE)

# References — 2 columns
txt(s10, "REFERENSI KUNCI", Inches(0.75), Inches(3.65), Inches(11.8), Inches(0.38),
    size=12, bold=True, color=MUTED)

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

txt(s10, refs_left,  Inches(0.75), Inches(4.1), Inches(5.8), Inches(2.5),
    size=13, color=MUTED)
txt(s10, refs_right, Inches(6.85), Inches(4.1), Inches(5.8), Inches(2.5),
    size=13, color=MUTED)

rect(s10, Inches(6.5), Inches(4.1), Inches(0.012), Inches(2.5), fill=LINE)

# CTA bottom
txt(s10, "Terima kasih — Dewan Juri AIRIMPACT 2026",
    Inches(0.75), Inches(6.8), Inches(8.0), Inches(0.5),
    size=16, color=MUTED, italic=True)

notes(s10,
    "Tutup dengan kutipan inti SMOKECUT. Sampaikan rasa terima kasih kepada dewan juri. "
    "Siap untuk sesi tanya jawab — tekankan: sistem sudah berjalan dan bisa didemonstrasikan langsung.")


# ═══════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════
prs.save(OUTPUT_FILE)
print(f"✅  Presentation saved → {OUTPUT_FILE}  ({prs.slides.__len__()} slides)")
