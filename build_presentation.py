"""AIRIMPACT 2026 — SMOKECUT Proposal Deck
Design: Modern Liquid Glassmorphism & Atmospheric Depth
- Ambient background (light periwinkle + soft orbs at corners)
- Frosted-glass cards (white fill, vivid glowing border, gloss top strip)
- Floating geometric accents (dot grids, plus marks, thin scan lines)
- Punchy, conversational copywriting — tech pitch tone
- Python 3.9 compatible (no match/case, from __future__ annotations)
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

# ── Atmospheric Background Palette ────────────────────────
BG_BASE    = RGBColor(220, 230, 255)   # #DCE6FF periwinkle blue base

# Orb colors (large soft ambient circles)
ORB_BLUE   = RGBColor(186, 215, 254)   # blue-200 brighter
ORB_VIOLET = RGBColor(210, 200, 254)   # violet-200
ORB_EMERALD= RGBColor(154, 236, 200)   # emerald-200
ORB_AMBER  = RGBColor(252, 220, 120)   # amber-200
ORB_ROSE   = RGBColor(252, 195, 200)   # rose-200

# Accent colors (vivid, for borders / text on glass)
BLUE    = RGBColor(37,  99,  235)   # blue-600
EMERALD = RGBColor(5,   150, 105)   # emerald-600
AMBER   = RGBColor(217, 119, 6)     # amber-600
ROSE    = RGBColor(220, 38,  38)    # rose-600
VIOLET  = RGBColor(124, 58,  237)   # violet-600
NAVY    = RGBColor(15,  23,  42)    # near-black heading

# Glass fill colors (near-white tints)
GLASS      = RGBColor(255, 255, 255)   # pure white glass
GLASS_BLUE = RGBColor(238, 246, 255)   # blue-tinted glass
GLASS_EMR  = RGBColor(236, 253, 245)   # emerald-tinted
GLASS_AMB  = RGBColor(255, 251, 230)   # amber-tinted
GLASS_ROSE = RGBColor(255, 240, 241)   # rose-tinted
GLASS_VIO  = RGBColor(245, 242, 255)   # violet-tinted

# Text
TEXT  = RGBColor(15,  23,  42)    # near-black
MUTED = RGBColor(71,  85, 105)    # slate-600
WHITE = RGBColor(255, 255, 255)

# Dot accent (subtle, matches BG slightly)
DOT_COLOR   = RGBColor(170, 196, 240)   # slightly more blue than BG
PLUS_COLOR  = RGBColor(180, 205, 245)
SCAN_COLOR  = RGBColor(195, 215, 248)   # thin scan lines

FONT = "Arial"


# ═══════════════════════════════════════════════════════════
# CORE DRAWING HELPERS
# ═══════════════════════════════════════════════════════════

def bg(slide):
    """Atmospheric base background."""
    r = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = BG_BASE
    r.line.fill.background()


def orb(slide, cx, cy, diam, color):
    """Soft ambient orb (large blurred-looking circle)."""
    r = diam / 2
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx - r, cy - r, diam, diam)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s


def add_orbs(slide, orb_defs):
    """Draw a list of (cx, cy, diam, color) orbs."""
    for cx, cy, diam, color in orb_defs:
        orb(slide, Inches(cx), Inches(cy), Inches(diam), color)


def add_dots(slide, ox, oy, cols=5, rows=4, spacing=0.33, color=DOT_COLOR, size=0.065):
    """Dot-grid floating accent."""
    for r in range(rows):
        for c in range(cols):
            x = Inches(ox + c * spacing)
            y = Inches(oy + r * spacing)
            d = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, Inches(size), Inches(size))
            d.fill.solid(); d.fill.fore_color.rgb = color
            d.line.fill.background()


def add_plus(slide, cx, cy, size=0.18, color=PLUS_COLOR):
    """Small plus/cross mark (drone-HUD motif)."""
    arm = Inches(size); thick = Inches(size * 0.28)
    cx_i = Inches(cx); cy_i = Inches(cy)
    for shape_args in [
        (cx_i - arm / 2, cy_i - thick / 2, arm, thick),
        (cx_i - thick / 2, cy_i - arm / 2, thick, arm),
    ]:
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, *shape_args)
        s.fill.solid(); s.fill.fore_color.rgb = color
        s.line.fill.background()


def add_scan_lines(slide, y_start=6.95, count=3, gap=0.14):
    """Thin HUD-style horizontal scan lines at bottom."""
    for i in range(count):
        y = Inches(y_start + i * gap)
        s = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.5), y, Inches(12.33), Inches(0.012))
        s.fill.solid(); s.fill.fore_color.rgb = SCAN_COLOR
        s.line.fill.background()


def glass_card(slide, left, top, width, height, fill=GLASS, border_color=BLUE, bw=Pt(2)):
    """Frosted-glass card with glossy top-highlight strip."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid(); card.fill.fore_color.rgb = fill
    card.line.color.rgb = border_color; card.line.width = bw
    # Glossy highlight at top
    gh = Inches(0.1)
    g = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left + Inches(0.12), top + Inches(0.09),
        width - Inches(0.24), gh)
    g.fill.solid(); g.fill.fore_color.rgb = WHITE
    g.line.fill.background()
    return card


def rrect(slide, left, top, width, height, fill=GLASS, border=None, bw=Pt(1.5)):
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border; r.line.width = bw
    else:
        r.line.fill.background()
    return r


def rect(slide, left, top, width, height, fill=GLASS, border=None, bw=Pt(0)):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if border:
        r.line.color.rgb = border; r.line.width = bw
    else:
        r.line.fill.background()
    return r


def circle_label(slide, cx, cy, diam, fill, label, size=24, color=WHITE, bold=True):
    r = diam / 2
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx - r, cy - r, diam, diam)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.fill.background()
    txt(slide, label, cx - r, cy - r, diam, diam,
        size=size, bold=bold, color=color, align=PP_ALIGN.CENTER)


def txt(slide, text, left, top, width, height,
        size=18, bold=False, color=TEXT, align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text; p.alignment = align
    p.font.name = FONT; p.font.size = Pt(size)
    p.font.bold = bold; p.font.color.rgb = color; p.font.italic = italic
    return tb, tf


def multiline(slide, lines, left, top, width, height, leading=Pt(5)):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text        = item[0]
        p.font.name   = FONT
        p.font.size   = Pt(item[1] if len(item) > 1 else 18)
        p.font.bold   = item[2] if len(item) > 2 else False
        p.font.color.rgb = item[3] if len(item) > 3 else TEXT
        p.alignment   = item[4] if len(item) > 4 else PP_ALIGN.LEFT
        p.space_after = leading


def divider(slide, left, top, width, color=DOT_COLOR):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.015))
    r.fill.solid(); r.fill.fore_color.rgb = color
    r.line.fill.background()


def tag(slide, label, left, top):
    txt(slide, "✦  " + label.upper(), left, top, Inches(10), Inches(0.35),
        size=11, bold=True, color=VIOLET)


def slide_title(slide, title_text, left=Inches(0.75), top=Inches(0.52),
                width=Inches(11.8), size=27, color=NAVY):
    txt(slide, title_text, left, top, width, Inches(0.9),
        size=size, bold=True, color=color)


def pill(slide, label, left, top, width=Inches(2.6),
         fill=GLASS, border=BLUE, text_color=NAVY, size=14):
    rrect(slide, left, top, width, Inches(0.42), fill=fill, border=border, bw=Pt(1.5))
    txt(slide, label, left, top + Inches(0.03), width, Inches(0.4),
        size=size, color=text_color, align=PP_ALIGN.CENTER)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


# Standard orb sets (reused across slides with variation)
def orbs_default(slide):
    add_orbs(slide, [
        (-0.8,  -0.8, 3.8, ORB_BLUE),
        (13.8,  -0.8, 3.2, ORB_VIOLET),
        (-0.8,  7.8,  3.5, ORB_EMERALD),
        (13.5,  7.5,  3.0, ORB_AMBER),
    ])


def accents_default(slide):
    add_dots(slide, 10.5, 1.2, cols=4, rows=3)
    add_plus(slide, 10.1, 5.8)
    add_plus(slide, 11.6, 2.5)
    add_scan_lines(slide)


# ═══════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# Navy-glass top bar + atmospheric orbs + floating accents
# ═══════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank)
bg(s1)

# Extra-dramatic orbs for cover
add_orbs(s1, [
    (-1.0, -1.0, 5.0, ORB_BLUE),
    (13.8, -0.5, 4.5, ORB_VIOLET),
    (-0.5,  7.8, 4.0, ORB_EMERALD),
    (13.0,  7.0, 3.8, ORB_AMBER),
    (6.5,  -1.5, 4.5, ORB_ROSE),    # top-center pink glow
])

# Floating accents
add_dots(s1, 9.4, 4.0, cols=5, rows=4, spacing=0.38)
add_plus(s1, 9.1, 3.8, size=0.22)
add_plus(s1, 11.8, 5.5, size=0.16)
add_plus(s1, 2.0, 5.8, size=0.14, color=ORB_VIOLET)

# Main glass card — left hero
glass_card(s1, Inches(0.6), Inches(0.6), Inches(8.4), Inches(6.3),
           fill=GLASS, border_color=BLUE, bw=Pt(2))

# SMOKECUT wordmark
txt(s1, "SMOKECUT",
    Inches(1.0), Inches(1.05), Inches(7.5), Inches(1.6),
    size=72, bold=True, color=NAVY)

# Short hook below wordmark
rect(s1, Inches(1.0), Inches(2.52), Inches(1.5), Inches(0.045), fill=BLUE)
txt(s1,
    "Ketika asap terlihat — sudah terlambat.",
    Inches(1.0), Inches(2.65), Inches(7.0), Inches(0.7),
    size=20, italic=True, color=VIOLET)

txt(s1,
    "Kami hadir sebelum asap pertama mengepul.\n"
    "Drone RGB biasa + AI kami = peta taktis sekat bakar\n"
    "yang melindungi jutaan paru-paru warga Indonesia.",
    Inches(1.0), Inches(3.45), Inches(7.0), Inches(1.6),
    size=18, color=MUTED)

# 3 quick-win pills inside hero card
quick_wins = [
    ("🤖  Computer Vision",   GLASS_BLUE, BLUE),
    ("🌿  Drone RGB — Murah", GLASS_EMR,  EMERALD),
    ("📢  Real-time Alert",   GLASS_AMB,  AMBER),
]
for i, (label, fill, border) in enumerate(quick_wins):
    pill(s1, label, Inches(1.0) + i * Inches(2.5), Inches(5.5),
         width=Inches(2.3), fill=fill, border=border, text_color=NAVY, size=13)

# Right side: event badge (floating glass card)
glass_card(s1, Inches(9.4), Inches(1.4), Inches(3.3), Inches(4.5),
           fill=GLASS_VIO, border_color=VIOLET, bw=Pt(2))
txt(s1, "AIRIMPACT",   Inches(9.4), Inches(1.75), Inches(3.3), Inches(0.6),
    size=16, bold=True, color=VIOLET, align=PP_ALIGN.CENTER)
txt(s1, "2026",        Inches(9.4), Inches(2.3),  Inches(3.3), Inches(1.2),
    size=72, bold=True, color=NAVY,   align=PP_ALIGN.CENTER)
txt(s1, "MarkPlus, Inc.",Inches(9.4), Inches(3.52), Inches(3.3), Inches(0.4),
    size=13, color=MUTED, align=PP_ALIGN.CENTER)
divider(s1, Inches(9.8), Inches(4.0), Inches(2.5), VIOLET)
multiline(s1, [
    ("Tim SMOKECUT",   13, True,  NAVY,  PP_ALIGN.CENTER),
    ("@Aam · @Apliy · @Indra", 12, False, MUTED, PP_ALIGN.CENTER),
], Inches(9.4), Inches(4.15), Inches(3.3), Inches(1.2), leading=Pt(6))

notes(s1,
    "Slide pembuka. Sampaikan nama tim, perkenalkan 3 anggota, dan langsung deliver hook: "
    "'Ketika asap terlihat, sudah terlambat.' SMOKECUT hadir sebelum itu terjadi.")


# ═══════════════════════════════════════════════════════════
# SLIDE 2 — EXECUTIVE SUMMARY
# 3 glass stat panels + 2-col pitch text
# ═══════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank)
bg(s2); orbs_default(s2); accents_default(s2)

tag(s2, "Executive Summary", Inches(0.75), Inches(0.28))
slide_title(s2, "Satu Drone. Tiga Algoritma. Nol Ruang untuk Asap.")
divider(s2, Inches(0.75), Inches(1.52), Inches(11.8))

# 3 glass stat cards
stats = [
    ("≥50%", "Kebakaran lahan\nbisa dicegah",          BLUE,    GLASS_BLUE, ORB_BLUE),
    ("100%", "Gratis untuk\ndesa & relawan MPA",        EMERALD, GLASS_EMR,  ORB_EMERALD),
    ("0 Rp", "Biaya hardware\ntambahan",                AMBER,   GLASS_AMB,  ORB_AMBER),
]
for i, (num, label, border, fill, _) in enumerate(stats):
    lx = Inches(0.75) + i * Inches(4.0)
    glass_card(s2, lx, Inches(1.65), Inches(3.7), Inches(2.0), fill=fill, border_color=border)
    txt(s2, num,   lx, Inches(1.72), Inches(3.7), Inches(1.1),
        size=54, bold=True, color=border, align=PP_ALIGN.CENTER)
    txt(s2, label, lx, Inches(2.82), Inches(3.7), Inches(0.72),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)

divider(s2, Inches(0.75), Inches(3.75), Inches(11.8))

# 2-col: Problem vs Solution
multiline(s2, [
    ("🔥  MASALAHNYA NYATA",         13, True,  ROSE, PP_ALIGN.LEFT),
    ("Karhutla Sumatera & Kalimantan melepaskan\nasap PM2.5 yang meracuni jutaan warga setiap\ntahun. Respons selalu reaktif, selalu terlambat.",
     17, False, MUTED, PP_ALIGN.LEFT),
], Inches(0.75), Inches(3.9), Inches(5.4), Inches(2.8))

rect(s2, Inches(6.45), Inches(3.9), Inches(0.012), Inches(2.5), fill=DOT_COLOR)

multiline(s2, [
    ("✅  SMOKECUT MEMBALIK PARADIGMA", 13, True, EMERALD, PP_ALIGN.LEFT),
    ("Analisis citra drone RGB secara offline:\ndeteksi asap dini (YOLO), pemetaan semak\nkering (VARI), rute sekat bakar wind-aware.",
     17, False, MUTED, PP_ALIGN.LEFT),
], Inches(6.75), Inches(3.9), Inches(5.65), Inches(2.8))

notes(s2,
    "Hook kuat: satu drone, tiga algoritma, nol kompromi. "
    "Tekankan bahwa SMOKECUT membalik paradigma dari reaktif ke preventif.")


# ═══════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM IDENTIFICATION
# 3 glass rows with orb-colored icon circles
# ═══════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank)
bg(s3); orbs_default(s3)
add_dots(s3, 11.0, 0.5, cols=3, rows=5, spacing=0.4)
add_plus(s3, 10.7, 4.2); add_plus(s3, 12.4, 1.6, size=0.14)

tag(s3, "01. Problem Identification", Inches(0.75), Inches(0.28))
slide_title(s3, "Indonesia: Hutan Terluas, Asap Terbanyak.")
divider(s3, Inches(0.75), Inches(1.52), Inches(11.8))

problems = [
    (ROSE,    GLASS_ROSE,  "🔥",
     "Kebakaran Tanpa Akhir",
     "Sumatera & Kalimantan kehilangan setara dua lapangan sepak bola setiap menit "
     "di puncak musim kering. Dan sistem respons kita masih berbasis walkie-talkie."),
    (AMBER,   GLASS_AMB,   "🌫",
     "PM2.5: Pembunuh Tak Kasat Mata",
     "ISPU Kalsel 2023: 3× ambang batas WHO. Klaim BPJS penyakit paru melonjak 40%. "
     "Jutaan orang menghirup udara yang seharusnya tidak layak dihirup."),
    (BLUE,    GLASS_BLUE,  "🛠",
     "Teknologi Ada, tapi Tak Sampai ke Lapangan",
     "Tim MPA bekerja buta — tanpa peta bahan bakar, tanpa arah angin, tanpa safety zone. "
     "Drone thermal Rp 80 juta? Jauh dari jangkauan anggaran desa manapun."),
]

for i, (color, fill, icon, title, body) in enumerate(problems):
    top = Inches(1.72) + i * Inches(1.68)
    glass_card(s3, Inches(0.75), top, Inches(11.83), Inches(1.48),
               fill=fill, border_color=color, bw=Pt(2))
    circle_label(s3, Inches(1.52), top + Inches(0.52), Inches(0.8), color, icon, 24, WHITE)
    txt(s3, title, Inches(2.3), top + Inches(0.1),  Inches(9.8), Inches(0.52),
        size=19, bold=True, color=NAVY)
    txt(s3, body,  Inches(2.3), top + Inches(0.6),  Inches(9.8), Inches(0.75),
        size=16, color=MUTED)

notes(s3,
    "Tiga krisis beruntun. Gunakan ritme dramatis: kebakaran → asap → teknologi gagal sampai. "
    "Analoginya sederhana: 'dua lapangan bola per menit' membuat angka ini terasa nyata.")


# ═══════════════════════════════════════════════════════════
# SLIDE 4 — ROOT CAUSE ANALYSIS
# Split glass panels: left causes | right impacts
# ═══════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank)
bg(s4); orbs_default(s4)
add_dots(s4, 0.4, 5.5, cols=4, rows=3, spacing=0.32, color=DOT_COLOR)
add_plus(s4, 0.7, 5.3, size=0.15); add_scan_lines(s4)

tag(s4, "01. Problem Analysis", Inches(0.75), Inches(0.28))
slide_title(s4, "Bukan Kurang Semangat. Kurang Sistem.")
divider(s4, Inches(0.75), Inches(1.52), Inches(11.8))

txt(s4, "MENGAPA SELALU TERLAMBAT?", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.4),
    size=12, bold=True, color=ROSE)

root_causes = [
    ("1", "Zero Fuel Map",        "Tanpa peta semak kering real-time, tim MPA tak bisa merencanakan sekat yang efektif."),
    ("2", "Hardware Gap",         "Drone thermal Rp 80 juta = mustahil. Padahal drone RGB Rp 6 juta sudah cukup, jika ada AI-nya."),
    ("3", "Perencanaan Intuitif", "Jalur babatan ditentukan 'kira-kira' — tanpa arah angin, tanpa safety buffer, tanpa data."),
]

for j, (num, title, body) in enumerate(root_causes):
    top = Inches(2.1) + j * Inches(1.5)
    glass_card(s4, Inches(0.75), top, Inches(5.65), Inches(1.3),
               fill=GLASS_ROSE, border_color=ROSE, bw=Pt(1.5))
    circle_label(s4, Inches(1.3), top + Inches(0.42), Inches(0.6), ROSE, num, 20, WHITE)
    txt(s4, title, Inches(2.0), top + Inches(0.05), Inches(4.2), Inches(0.46),
        size=17, bold=True, color=NAVY)
    txt(s4, body,  Inches(2.0), top + Inches(0.5),  Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

rect(s4, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=DOT_COLOR)
txt(s4, "DAMPAK KASATMATA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.4),
    size=12, bold=True, color=AMBER)

impacts = [
    ("📉", "Respons lapangan tertunda 4–8 jam dari idealnya"),
    ("🏥", "Biaya kesehatan PM2.5 nasional tembus Rp 1,9 triliun/tahun"),
    ("🌿", "100.000+ ha lahan gambut hangus per tahun (2020–2024 avg.)"),
    ("📡", "0% desa terdampak punya sistem monitoring berbasis data"),
    ("🧯", "MPA tak jarang babat jalur yang justru mempercepat rambat api"),
]

for k, (ico, body) in enumerate(impacts):
    top = Inches(2.1) + k * Inches(0.98)
    glass_card(s4, Inches(6.85), top, Inches(5.65), Inches(0.78),
               fill=GLASS_AMB, border_color=AMBER, bw=Pt(1))
    txt(s4, ico,  Inches(7.1),  top + Inches(0.1), Inches(0.5),  Inches(0.5), size=18)
    txt(s4, body, Inches(7.65), top + Inches(0.1), Inches(5.0),  Inches(0.55),
        size=15, color=MUTED)

notes(s4,
    "Tiga akar masalah → lima dampak terukur. Tekankan: ini bukan soal motivasi, "
    "ini soal ketiadaan infrastruktur data di garis depan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 5 — PROPOSED SOLUTION
# Left 3-step pipeline | Right dashboard image in glass frame
# ═══════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank)
bg(s5); orbs_default(s5)
add_dots(s5, 0.5, 1.2, cols=3, rows=4, spacing=0.35)
add_plus(s5, 0.8, 5.5, size=0.16, color=PLUS_COLOR)

tag(s5, "02. Proposed Solution", Inches(0.75), Inches(0.28))
slide_title(s5, "SEKAT-AI: Video Drone → Peta Taktis dalam 120 Detik.")
divider(s5, Inches(0.75), Inches(1.52), Inches(11.8))

steps = [
    (BLUE,    GLASS_BLUE,  "01", "Deteksi Asap & Api Dini",
     "YOLOv8n mengidentifikasi kepulan asap mikro dan heat-spot\npada frame udara. Tanpa thermal. Hanya kamera RGB."),
    (AMBER,   GLASS_AMB,   "02", "Peta Semak Kering via VARI",
     "Formula VARI = (G−R)/(G+R−B) mewarnai setiap piksel:\nmerah = bahan bakar aktif, hijau = zona aman."),
    (EMERALD, GLASS_EMR,   "03", "Rute Sekat Bakar Optimal",
     "Algoritma wind-aware kalkulasi jalur potong terpendek,\nkunci safety buffer ≥25 m, hubungkan hambatan alami."),
]

for i, (color, fill, num, title, body) in enumerate(steps):
    top = Inches(1.72) + i * Inches(1.68)
    glass_card(s5, Inches(0.75), top, Inches(6.3), Inches(1.48),
               fill=fill, border_color=color, bw=Pt(2))
    circle_label(s5, Inches(1.3), top + Inches(0.5), Inches(0.72), color, num, 16, WHITE, True)
    txt(s5, title, Inches(2.1), top + Inches(0.1), Inches(4.7), Inches(0.5),
        size=18, bold=True, color=NAVY)
    txt(s5, body,  Inches(2.1), top + Inches(0.6), Inches(4.7), Inches(0.8),
        size=15, color=MUTED)

# Dashboard image in glass frame
img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "dashboard_mockup.png")
glass_card(s5, Inches(7.35), Inches(1.62), Inches(5.6), Inches(5.52),
           fill=GLASS_BLUE, border_color=BLUE, bw=Pt(2))
if os.path.exists(img_path):
    s5.shapes.add_picture(img_path, Inches(7.5), Inches(1.85), Inches(5.3), Inches(4.8))
else:
    txt(s5, "[ Dashboard Preview ]",
        Inches(7.35), Inches(3.8), Inches(5.6), Inches(0.6),
        size=18, color=MUTED, align=PP_ALIGN.CENTER)

# VARI formula badge
glass_card(s5, Inches(7.5), Inches(6.6), Inches(5.0), Inches(0.42),
           fill=GLASS_BLUE, border_color=BLUE, bw=Pt(1))
txt(s5, "  VARI = (G − R) / (G + R − B)",
    Inches(7.6), Inches(6.63), Inches(4.8), Inches(0.35),
    size=13, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

notes(s5,
    "Pipeline tiga lapis: (1) YOLO deteksi asap → (2) VARI petakan bahan bakar → "
    "(3) Algoritma sekat taktis. Semua berjalan lokal, offline, di laptop lapangan.")


# ═══════════════════════════════════════════════════════════
# SLIDE 6 — FIELD EXECUTION
# 4 glass step columns with large numbered circles
# ═══════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank)
bg(s6); orbs_default(s6)
add_dots(s6, 11.5, 5.5, cols=3, rows=4, spacing=0.33)
add_plus(s6, 11.2, 5.3, size=0.15); add_scan_lines(s6)

tag(s6, "03. Field Execution", Inches(0.75), Inches(0.28))
slide_title(s6, "4 Langkah. 1 Tim. Nol Kompromi.")
divider(s6, Inches(0.75), Inches(1.52), Inches(11.8))

cols = [
    (BLUE,    GLASS_BLUE, "01", "TERBANG\n& REKAM",
     "Drone RGB standar terbang 60–100 m. File video dikirim ke laptop via USB / WiFi lokal."),
    (AMBER,   GLASS_AMB,  "02", "UPLOAD\n& PROSES",
     "SEKAT-AI Engine menganalisis: deteksi asap, heatmap VARI, kalkulasi rute. Kurang dari 2 menit."),
    (EMERALD, GLASS_EMR,  "03", "BABAT\nSEKAT",
     "Peta GPS langsung ke HP anggota MPA via WhatsApp. Tim babat jalur berdasar data, bukan naluri."),
    (ROSE,    GLASS_ROSE, "04", "ALERT\nWARGA",
     "Notifikasi otomatis ke warga downwind: estimasi PM2.5, arah asap, zona aman evakuasi."),
]

col_w = Inches(2.8); col_gap = Inches(0.35)
for i, (color, fill, num, title, body) in enumerate(cols):
    lx = Inches(0.75) + i * (col_w + col_gap)
    glass_card(s6, lx, Inches(1.72), col_w, Inches(4.5), fill=fill, border_color=color, bw=Pt(2))
    circle_label(s6, lx + col_w / 2, Inches(2.42), Inches(1.05), color, num, 26, WHITE)
    txt(s6, title, lx, Inches(3.1),   col_w, Inches(0.75),
        size=17, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    txt(s6, body,  lx + Inches(0.1), Inches(3.95), col_w - Inches(0.2), Inches(2.0),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)
    if i < 3:
        txt(s6, "→", lx + col_w + col_gap * 0.5 - Inches(0.1), Inches(2.2),
            Inches(0.25), Inches(0.5), size=20, color=DOT_COLOR, align=PP_ALIGN.CENTER)

# Tech pills at bottom
tech_tags = ["FastAPI + Uvicorn", "YOLOv8n ONNX", "OpenCV / VARI", "WhatsApp Gateway"]
for i, t in enumerate(tech_tags):
    pill(s6, t, Inches(0.75) + i * Inches(3.17), Inches(6.55),
         width=Inches(2.7), fill=GLASS, border=DOT_COLOR, text_color=MUTED, size=13)

notes(s6,
    "4 langkah operasional yang bisa dijalankan relawan non-teknis dalam 20 menit pelatihan. "
    "Tekankan: antarmuka dibuat semudah mungkin — no coding, no manual, just upload and act.")


# ═══════════════════════════════════════════════════════════
# SLIDE 7 — IMPLEMENTATION TIMELINE
# Horizontal glass timeline + partner pills
# ═══════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank)
bg(s7); orbs_default(s7)
add_dots(s7, 0.5, 1.2, cols=3, rows=4, spacing=0.33)
add_plus(s7, 0.8, 4.5, size=0.15); add_scan_lines(s7)

tag(s7, "04. Implementation Plan", Inches(0.75), Inches(0.28))
slide_title(s7, "6 Bulan Membuktikan. Selamanya Berdampak.")
divider(s7, Inches(0.75), Inches(1.52), Inches(11.8))

milestones = [
    (BLUE,    GLASS_BLUE, "Bulan 1–2", "Setup & Pelatihan",
     "Instalasi di 2 desa pilot, kalibrasi model YOLO, latih MPA operasi drone & baca peta."),
    (AMBER,   GLASS_AMB,  "Bulan 3",   "Pilot Pemetaan Perdana",
     "Flight perdana. Generate peta VARI & rute sekat bakar. Uji dispatch WhatsApp ke HP MPA."),
    (EMERALD, GLASS_EMR,  "Bulan 4–5", "Implementasi Sekat",
     "MPA babat jalur berdasar peta digital. Monitor kualitas udara sebelum & sesudah babatan."),
    (ROSE,    GLASS_ROSE, "Bulan 6",   "Evaluasi & Replikasi",
     "Laporan dampak terukur. Sempurnakan model. Siapkan dokumentasi untuk 10 desa berikutnya."),
]

line_y = Inches(3.15)
rect(s7, Inches(0.75), line_y - Inches(0.012), Inches(11.8), Inches(0.025), fill=DOT_COLOR)
dot_xs = [Inches(1.6), Inches(4.6), Inches(7.6), Inches(10.6)]

for i, (color, fill, period, phase, body) in enumerate(milestones):
    x = dot_xs[i]
    # Dot on spine
    s = s7.shapes.add_shape(MSO_SHAPE.OVAL, x - Inches(0.18), line_y - Inches(0.18),
                             Inches(0.36), Inches(0.36))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background()
    # Content above/below alternating
    if i % 2 == 0:
        glass_card(s7, x - Inches(1.3), Inches(1.68), Inches(2.6), Inches(1.35),
                   fill=fill, border_color=color, bw=Pt(1.5))
        txt(s7, period, x - Inches(1.3), Inches(1.73), Inches(2.6), Inches(0.38),
            size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(2.08), Inches(2.6), Inches(0.42),
            size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(2.52), Inches(2.6), Inches(0.5),
            size=13, color=MUTED, align=PP_ALIGN.CENTER)
    else:
        glass_card(s7, x - Inches(1.3), Inches(3.42), Inches(2.6), Inches(1.35),
                   fill=fill, border_color=color, bw=Pt(1.5))
        txt(s7, period, x - Inches(1.3), Inches(3.47), Inches(2.6), Inches(0.38),
            size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s7, phase,  x - Inches(1.3), Inches(3.82), Inches(2.6), Inches(0.42),
            size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s7, body,   x - Inches(1.3), Inches(4.26), Inches(2.6), Inches(0.5),
            size=13, color=MUTED, align=PP_ALIGN.CENTER)

divider(s7, Inches(0.75), Inches(5.75), Inches(11.8))
txt(s7, "MITRA KUNCI", Inches(0.75), Inches(5.88), Inches(2.0), Inches(0.35),
    size=11, bold=True, color=MUTED)
partners = ["Dinas Kehutanan", "BPBD Setempat", "Dana Desa", "CSR Perkebunan"]
for i, p in enumerate(partners):
    pill(s7, p, Inches(2.95) + i * Inches(2.65), Inches(5.88),
         width=Inches(2.3), fill=GLASS, border=DOT_COLOR, text_color=MUTED, size=13)

notes(s7,
    "Tekankan bahwa Bulan 6 bukan garis finish — itu starting point untuk replikasi ke 10 desa. "
    "Model bisnis cross-subsidy membuat ekspansi tidak bergantung pada satu sumber dana.")


# ═══════════════════════════════════════════════════════════
# SLIDE 8 — RESOURCES & RISK MITIGATION
# 2-col: green glass left | rose glass right
# ═══════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank)
bg(s8); orbs_default(s8)
add_dots(s8, 11.0, 2.0, cols=4, rows=5, spacing=0.33)
add_plus(s8, 10.7, 1.8, size=0.15); add_scan_lines(s8)

tag(s8, "04. Resources & Risk", Inches(0.75), Inches(0.28))
slide_title(s8, "Lean by Design. Bulletproof by Engineering.")
divider(s8, Inches(0.75), Inches(1.52), Inches(11.8))

txt(s8, "YANG KAMI BUTUHKAN", Inches(0.75), Inches(1.65), Inches(5.6), Inches(0.4),
    size=12, bold=True, color=EMERALD)

resources = [
    ("💻", "Laptop Lapangan (RAM ≥8 GB)",
     "Sudah dimiliki sebagian besar tim MPA & dinas. Tidak perlu beli perangkat baru."),
    ("🚁", "Drone Kamera RGB (≥1080p)",
     "DJI Mini 2 mulai Rp 5–7 juta. Nol biaya drone thermal. Nol kompromi kualitas."),
    ("📶", "Internet? Opsional.",
     "Sistem offline-first. Alert WA diantrikan secara otomatis, kirim begitu sinyal ada."),
]

for j, (ico, title, body) in enumerate(resources):
    top = Inches(2.1) + j * Inches(1.5)
    glass_card(s8, Inches(0.75), top, Inches(5.65), Inches(1.3),
               fill=GLASS_EMR, border_color=EMERALD, bw=Pt(1.5))
    circle_label(s8, Inches(1.3), top + Inches(0.42), Inches(0.6), EMERALD, ico, 16, WHITE)
    txt(s8, title, Inches(2.0), top + Inches(0.05), Inches(4.2), Inches(0.46),
        size=17, bold=True, color=NAVY)
    txt(s8, body,  Inches(2.0), top + Inches(0.5),  Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

rect(s8, Inches(6.6), Inches(1.65), Inches(0.012), Inches(5.3), fill=DOT_COLOR)
txt(s8, "RISIKO & MITIGASINYA", Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.4),
    size=12, bold=True, color=ROSE)

risks = [
    ("1", "Blank Spot Sinyal",
     "SEKAT-AI 100% offline. Alert WA diantrikan, kirim otomatis saat sinyal muncul."),
    ("2", "Keselamatan MPA",
     "Safety buffer ≥25–35 m dari api aktif dikunci otomatis oleh algoritma. No manual override."),
    ("3", "False Positive Deteksi",
     "Human-in-the-loop: setiap alert butuh konfirmasi 1 klik dari koordinator lapangan."),
]

for k, (num, title, body) in enumerate(risks):
    top = Inches(2.1) + k * Inches(1.5)
    glass_card(s8, Inches(6.85), top, Inches(5.65), Inches(1.3),
               fill=GLASS_ROSE, border_color=ROSE, bw=Pt(1.5))
    circle_label(s8, Inches(7.4), top + Inches(0.42), Inches(0.6), ROSE, num, 20, WHITE)
    txt(s8, title, Inches(8.1), top + Inches(0.05), Inches(4.2), Inches(0.46),
        size=17, bold=True, color=NAVY)
    txt(s8, body,  Inches(8.1), top + Inches(0.5),  Inches(4.2), Inches(0.65),
        size=14, color=MUTED)

notes(s8,
    "Lean by design: tidak ada pembelian perangkat mahal. Bulletproof by engineering: "
    "tiga risiko utama telah dimitigasi secara teknis sebelum sistem go-live.")


# ═══════════════════════════════════════════════════════════
# SLIDE 9 — IMPACT & SUSTAINABILITY
# Large glass stat panels + KPI + sustainability split
# ═══════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank)
bg(s9); orbs_default(s9)
add_dots(s9, 11.0, 0.5, cols=4, rows=4, spacing=0.35)
add_plus(s9, 10.7, 0.4, size=0.15); add_scan_lines(s9)

tag(s9, "06. Expected Impact & Sustainability", Inches(0.75), Inches(0.28))
slide_title(s9, "Angka-Angka yang Bicara Lebih Keras dari Presentasi Apapun.")
divider(s9, Inches(0.75), Inches(1.52), Inches(11.8))

impact_stats = [
    ("≥50%", "Kebakaran lahan\ntercegah (pilot 6 bulan)", BLUE,    GLASS_BLUE),
    ("≥80%", "Babatan sekat\nberbasis data peta VARI",    EMERALD, GLASS_EMR),
    ("100%", "Biomassa jadi\nkompos / pakan ternak",       AMBER,   GLASS_AMB),
]

for i, (num, label, color, fill) in enumerate(impact_stats):
    lx = Inches(0.75) + i * Inches(4.0)
    glass_card(s9, lx, Inches(1.65), Inches(3.7), Inches(2.1), fill=fill, border_color=color, bw=Pt(2))
    txt(s9, num,   lx, Inches(1.72), Inches(3.7), Inches(1.1),
        size=56, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(s9, label, lx, Inches(2.82), Inches(3.7), Inches(0.75),
        size=14, color=MUTED, align=PP_ALIGN.CENTER)

divider(s9, Inches(0.75), Inches(3.9), Inches(11.8))
txt(s9, "OUTPUT TERUKUR (PILOT 6 BULAN)", Inches(0.75), Inches(4.05),
    Inches(11.8), Inches(0.4), size=12, bold=True, color=MUTED)
txt(s9,
    "• 2 desa terpetakan penuh dengan peta semak kering per musim kemarau\n"
    "• ≥20 anggota MPA tersertifikasi operasi drone & interpretasi peta digital\n"
    "• Jalur sekat bakar terbangun di 100% zona semak merah teridentifikasi",
    Inches(0.75), Inches(4.5), Inches(11.8), Inches(1.0),
    size=17, color=MUTED)

divider(s9, Inches(0.75), Inches(5.52), Inches(11.8))
txt(s9, "MODEL KEBERLANJUTAN  —  CROSS-SUBSIDY", Inches(0.75), Inches(5.65),
    Inches(6.0), Inches(0.4), size=12, bold=True, color=MUTED)

glass_card(s9, Inches(0.75), Inches(6.08), Inches(4.5), Inches(0.95),
           fill=GLASS_EMR, border_color=EMERALD, bw=Pt(1.5))
txt(s9, "🌿  GRATIS — Desa & MPA",
    Inches(0.75), Inches(6.14), Inches(4.5), Inches(0.42),
    size=15, bold=True, color=EMERALD, align=PP_ALIGN.CENTER)
txt(s9, "Didanai Dana Desa Tanggap Bencana",
    Inches(0.75), Inches(6.58), Inches(4.5), Inches(0.35),
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

glass_card(s9, Inches(5.6), Inches(6.08), Inches(4.8), Inches(0.95),
           fill=GLASS_AMB, border_color=AMBER, bw=Pt(1.5))
txt(s9, "💼  BERBAYAR — Korporasi & Dinas",
    Inches(5.6), Inches(6.14), Inches(4.8), Inches(0.42),
    size=15, bold=True, color=AMBER, align=PP_ALIGN.CENTER)
txt(s9, "CSR Perkebunan & Dinas Lingkungan Hidup",
    Inches(5.6), Inches(6.58), Inches(4.8), Inches(0.35),
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

notes(s9,
    "Impact slide: angka adalah senjata utama. ≥50% kebakaran tercegah adalah klaim yang bisa dibuktikan. "
    "Cross-subsidy model: komunitas 100% gratis, biaya ditanggung oleh yang mampu.")


# ═══════════════════════════════════════════════════════════
# SLIDE 10 — CONCLUSION & REFERENCES
# Large glass quote card + 2-col references + closing
# ═══════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank)
bg(s10)

# More dramatic, different orb layout for closing
add_orbs(s10, [
    (-1.0, -1.0, 5.5, ORB_VIOLET),
    (13.5, -0.8, 4.0, ORB_BLUE),
    (-0.8,  7.5, 4.5, ORB_AMBER),
    (13.0,  7.0, 4.5, ORB_EMERALD),
    (6.0,   8.2, 5.0, ORB_ROSE),   # bottom-center glow
])
add_dots(s10, 10.5, 0.6, cols=4, rows=3, spacing=0.38)
add_plus(s10, 10.3, 0.5, size=0.18, color=PLUS_COLOR)
add_plus(s10, 12.2, 2.5, size=0.14, color=ORB_VIOLET)

# SMOKECUT wordmark
txt(s10, "SMOKECUT",
    Inches(0.75), Inches(0.4), Inches(4.0), Inches(0.6),
    size=16, bold=True, color=VIOLET)
txt(s10, "✦  AIRIMPACT 2026",
    Inches(5.0), Inches(0.42), Inches(4.0), Inches(0.5),
    size=12, bold=True, color=MUTED)

divider(s10, Inches(0.75), Inches(1.08), Inches(11.8), color=VIOLET)

# Central glass quote card
glass_card(s10, Inches(0.75), Inches(1.3), Inches(11.83), Inches(2.4),
           fill=GLASS_VIO, border_color=VIOLET, bw=Pt(2.5))
txt(s10,
    "\u201cUdara bersih bukan kemewahan.\n"
    "Kita bisa — dan wajib — memperjuangkannya\n"
    "dengan data, bukan harapan.\u201d",
    Inches(1.0), Inches(1.55), Inches(11.33), Inches(1.6),
    size=28, bold=True, color=NAVY, align=PP_ALIGN.CENTER, italic=True)

txt(s10, "— Tim SMOKECUT, AIRIMPACT 2026",
    Inches(0.75), Inches(3.82), Inches(11.83), Inches(0.42),
    size=14, color=VIOLET, align=PP_ALIGN.CENTER)

divider(s10, Inches(0.75), Inches(4.32), Inches(11.8), color=DOT_COLOR)

txt(s10, "REFERENSI KUNCI", Inches(0.75), Inches(4.45), Inches(11.8), Inches(0.38),
    size=11, bold=True, color=MUTED)

refs_left = (
    "1. MarkPlus, Inc. (2025). Survei Persepsi Masyarakat terhadap Kualitas Udara "
    "(Guidebook AIRIMPACT 2026).\n"
    "2. IQAir. (2026). Jabodetabek Air Quality Snapshot, 29 Oktober 2026.\n"
    "3. RCCC UI. (2023). Kajian Klaim BPJS Kesehatan Terkait Penyakit Polusi Udara di Jakarta."
)
refs_right = (
    "4. Permen LHK No. 28 Tahun 2021 tentang Sistem Pengendalian Kebakaran Hutan & Lahan.\n"
    "5. Gitelson, A.A., et al. (2002). Novel Algorithms for Remote Estimation of Vegetation "
    "Fraction (VARI). Remote Sensing of Environment.\n"
    "6. USDA Forest Service. (2018). Fire Management Guidelines: Fuel Breaks & Safety Zones."
)

glass_card(s10, Inches(0.75), Inches(4.88), Inches(5.8), Inches(2.1),
           fill=GLASS, border_color=DOT_COLOR, bw=Pt(1))
txt(s10, refs_left,  Inches(0.95), Inches(5.0), Inches(5.4), Inches(1.85),
    size=13, color=MUTED)

glass_card(s10, Inches(6.85), Inches(4.88), Inches(5.8), Inches(2.1),
           fill=GLASS, border_color=DOT_COLOR, bw=Pt(1))
txt(s10, refs_right, Inches(7.05), Inches(5.0), Inches(5.4), Inches(1.85),
    size=13, color=MUTED)

txt(s10, "Terima kasih — Dewan Juri AIRIMPACT 2026",
    Inches(0.75), Inches(7.07), Inches(8.0), Inches(0.35),
    size=15, color=MUTED, italic=True)

notes(s10,
    "Tutup dengan kutipan inti yang kuat. Siapkan untuk Q&A. "
    "Tekankan: sistem SMOKECUT sudah berjalan dan siap didemonstrasikan langsung di depan juri.")


# ═══════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════
prs.save(OUTPUT_FILE)
print(f"✅  Presentation saved → {OUTPUT_FILE}  ({len(prs.slides)} slides)")
