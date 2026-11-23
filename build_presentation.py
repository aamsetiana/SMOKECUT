"""Generates the official 10-slide PPTX proposal for AIRIMPACT 2026.

Strictly follows Guidebook rules:
- Format: .pptx
- Ratio: Landscape 16:9 (13.333" x 7.5")
- Length: Exactly 10 slides
- Typography: Body >= 18pt, References >= 12pt, Headings 24-36pt
- Theme: Dark Modern Geospatial (Navy #0B1120, Cards #1E293B, Sky Blue #38BDF8, Amber #F59E0B)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = "AIRIMPACT2026_SMOKECUT_Proposal.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

blank_slide_layout = prs.slide_layouts[6]

# Theme Colors
COLOR_BG = RGBColor(11, 17, 32)        # #0B1120 Deep Dark Slate
COLOR_CARD = RGBColor(30, 41, 59)      # #1E293B Slate Card
COLOR_BORDER = RGBColor(51, 65, 85)    # #334155 Slate Border
COLOR_TEXT_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
COLOR_SKY = RGBColor(56, 189, 248)     # #38BDF8 Electric Sky Blue
COLOR_AMBER = RGBColor(245, 158, 11)   # #F59E0B Warm Amber
COLOR_ROSE = RGBColor(239, 68, 68)     # #EF4444 Danger Rose
COLOR_EMERALD = RGBColor(16, 185, 129) # #10B981 Success Emerald

FONT_HEADING = "Arial"
FONT_BODY = "Arial"


def add_background(slide):
    """Sets slide solid dark navy background."""
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG
    bg_shape.line.fill.background()
    return bg_shape


def add_header(slide, tag_text, title_text):
    """Adds uniform modern header to slide."""
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    # Tag / Category
    p_tag = tf.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_SKY
    p_tag.space_after = Pt(2)

    # Main Slide Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(25)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_WHITE


def add_card(slide, left, top, width, height, title="", border_color=COLOR_BORDER):
    """Adds a dark card container with optional border and title."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.color.rgb = COLOR_SKY
    return card


# ==========================================================
# SLIDE 1: COVER
# ==========================================================
s1 = prs.slides.add_slide(blank_slide_layout)
add_background(s1)

# Subtle decorative banner
accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(1.2), Inches(0.08))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = COLOR_SKY
accent_bar.line.fill.background()

# Title text box
tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(3.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.text = "SMOKECUT"
p1.font.name = FONT_HEADING
p1.font.size = Pt(46)
p1.font.bold = True
p1.font.color.rgb = COLOR_TEXT_WHITE
p1.space_after = Pt(8)

p2 = tf1.add_paragraph()
p2.text = "Software Computer Vision Berbasis Drone Standar untuk Pemetaan Sekat Bakar Preventif & Pencegahan Asap PM2.5"
p2.font.name = FONT_BODY
p2.font.size = Pt(21)
p2.font.color.rgb = COLOR_TEXT_MUTED
p2.space_after = Pt(14)

p3 = tf1.add_paragraph()
p3.text = "“Cegah Api Melebar, Jaga Napas Warga”"
p3.font.name = FONT_BODY
p3.font.size = Pt(19)
p3.font.bold = True
p3.font.color.rgb = COLOR_AMBER

# Team details card
card_meta = add_card(s1, Inches(0.8), Inches(4.8), Inches(11.7), Inches(1.9), border_color=COLOR_SKY)
tb_meta = s1.shapes.add_textbox(Inches(1.1), Inches(5.0), Inches(11.1), Inches(1.5))
tf_m = tb_meta.text_frame
tf_m.word_wrap = True

pm1 = tf_m.paragraphs[0]
pm1.text = "TIM PENGEMBANG: SMOKECUT  |  KOMPETISI: AIRIMPACT 2026 (MarkPlus, Inc.)"
pm1.font.size = Pt(14)
pm1.font.bold = True
pm1.font.color.rgb = COLOR_SKY
pm1.space_after = Pt(6)

pm2 = tf_m.add_paragraph()
pm2.text = "• Aam Setiana (Ketua Tim, Project Manager & System Architect)\n• Apliy (Backend & Computer Vision Engineer)\n• Indra (Frontend & UI/UX Engineer)"
pm2.font.size = Pt(18)
pm2.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 2: 01. EXECUTIVE SUMMARY
# ==========================================================
s2 = prs.slides.add_slide(blank_slide_layout)
add_background(s2)
add_header(s2, "01. Executive Summary", "Memutus Rambat Api Sebelum Asap PM2.5 Mengancam Warga")

# 3 Column Cards
card_w = Inches(3.7)
card_h = Inches(4.8)
col_top = Inches(1.8)

# Card 1: Masalah
add_card(s2, Inches(0.8), col_top, card_w, card_h, "MASALAH", border_color=COLOR_ROSE)
tb = s2.shapes.add_textbox(Inches(1.05), col_top + Inches(0.8), card_w - Inches(0.5), card_h - Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Kebakaran semak terbuka menyumbang 15–20% emisi PM2.5 lokal langsung ke permukiman warga.\n\n• Deteksi satelit kerap memiliki jeda orbit dan resolusi kasar, membuat penanganan selalu terlambat dan reaktif saat api sudah membesar."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Card 2: Solusi
add_card(s2, Inches(4.8), col_top, card_w, card_h, "SOLUSI (SMOKECUT)", border_color=COLOR_SKY)
tb = s2.shapes.add_textbox(Inches(5.05), col_top + Inches(0.8), card_w - Inches(0.5), card_h - Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Solusi software murni (drone-agnostic) di atas kamera RGB biasa tanpa sensor thermal mahal.\n\n• Otomatis memetakan semak kering (VARI), mendeteksi asap dini, dan memandu rute sekat bakar optimal tim MPA selebar 3–5 meter."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Card 3: Target Pilot
add_card(s2, Inches(8.8), col_top, card_w, card_h, "TARGET PILOT (6 BULAN)", border_color=COLOR_EMERALD)
tb = s2.shapes.add_textbox(Inches(9.05), col_top + Inches(0.8), card_w - Inches(0.5), card_h - Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Uji coba di 2 desa rawan karhutla.\n\n• Target penurunan luas lahan terbakar ≥ 50%.\n\n• 20+ personel Masyarakat Peduli Api (MPA) terlatih.\n\n• Perlindungan dini warga di zona arah angin (downwind)."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 3: 02. PROBLEM IDENTIFICATION
# ==========================================================
s3 = prs.slides.add_slide(blank_slide_layout)
add_background(s3)
add_header(s3, "02. Problem Identification", "Api Skala Mikro yang Lolos Satelit Menjadi Bom Asap PM2.5")

p_cards = [
    ("Bahaya Tak Kasat Mata PM2.5", "Partikel halus PM2.5 (≤ 2.5 µm) menembus saluran napas hingga aliran darah, memicu ISPA, asma, dan gangguan kardiovaskular. Klaim BPJS Kesehatan 2023 untuk penyakit terkait polusi di Jakarta mencapai Rp1,2 Triliun (RCCC UI).", COLOR_ROSE),
    ("Kesenjangan Perilaku Masyarakat", "Berdasarkan Survei MarkPlus (2025), masyarakat masih dominan pasif menghadapi polusi (55,1% memakai masker). Tindakan pencegahan pada sumber (tidak membakar 33,7%) dan pemantauan udara (28,0%) masih sangat rendah.", COLOR_AMBER),
    ("Celah Penanganan Satelit Hotspot", "Satelit pemantau panas memiliki jeda lintasan orbit berjam-jam dan resolusi spasial kasar. Akibatnya, pembakaran semak lokal di pinggir desa baru terdeteksi setelah api membesar dan asap telah mengepung warga.", COLOR_SKY)
]

for idx, (title, desc, color) in enumerate(p_cards):
    top_pos = Inches(1.8 + idx * 1.7)
    add_card(s3, Inches(0.8), top_pos, Inches(11.7), Inches(1.45), border_color=color)
    tb = s3.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = f"{idx+1}. {title}"
    p1.font.bold = True
    p1.font.size = Pt(19)
    p1.font.color.rgb = color
    p1.space_after = Pt(3)

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 4: 03. PROBLEM ANALYSIS
# ==========================================================
s4 = prs.slides.add_slide(blank_slide_layout)
add_background(s4)
add_header(s4, "03. Problem Analysis", "Akar Masalah Lapangan & Target Perubahan Perilaku")

col_w = Inches(5.65)
col_h = Inches(4.8)

# Left Column: Akar Masalah
add_card(s4, Inches(0.8), Inches(1.8), col_w, col_h, "AKAR MASALAH DI LAPANGAN", border_color=COLOR_ROSE)
tb = s4.shapes.add_textbox(Inches(1.05), Inches(2.6), col_w - Inches(0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. Buta Medan dari Darat:\nRelawan MPA/warga tidak tahu batas hamparan semak kering dan arah rambat tercepat saat berada di lokasi.\n\n2. Teknologi Drone Terlalu Mahal:\nDrone thermal pemadam komersial berharga puluhan–ratusan juta rupiah, tidak terjangkau anggaran desa.\n\n3. Biomassa Jadi Bahan Bakar Baru:\nHasil babatan semak sering dibiarkan menumpuk di batas lahan sehingga kembali kering dan mudah tersulut."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Right Column: Target & Perilaku
add_card(s4, Inches(6.85), Inches(1.8), col_w, col_h, "TARGET & PERUBAHAN PERILAKU", border_color=COLOR_EMERALD)
tb = s4.shapes.add_textbox(Inches(7.1), Inches(2.6), col_w - Inches(0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Pengguna Utama:\nMasyarakat Peduli Api (MPA), Perangkat Desa, dan personel BPBD tingkat kecamatan.\n\n• Penerima Manfaat Langsung:\nWarga permukiman di zona arah angin (downwind), terutama kelompok rentan (anak, lansia, ibu hamil).\n\n• Perubahan Pola Perilaku:\nTransformasi dari pemadaman panik reaktif setelah asap mengepung → patroli preventif dan pembabatan sekat bakar terukur berbasis data citra drone."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 5: 04. PROPOSED SOLUTION (CARA KERJA & MOCKUP)
# ==========================================================
s5 = prs.slides.add_slide(blank_slide_layout)
add_background(s5)
add_header(s5, "04. Proposed Solution", "SMOKECUT: Ubah Drone Biasa Menjadi Pemandu Sekat Bakar Cerdas")

# Left Column: Workflow (40% width)
add_card(s5, Inches(0.8), Inches(1.8), Inches(4.8), Inches(4.8), "ALUR KERJA (PURE SOFTWARE)", border_color=COLOR_SKY)
tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.6), Inches(4.3), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. Rekam & Unggah:\nDrone RGB biasa terbang 60–100m. Video/foto diunggah ke SMOKECUT (bisa offline di laptop lapangan).\n\n2. Analisis Vision AI:\n• Deteksi dini titik api & mikro-asap.\n• Formula VARI = (G - R) / (G + R - B) memetakan semak kering tanpa sensor thermal.\n\n3. Rekomendasi Jalur Sekat:\nMemadukan peta semak + arah angin untuk menghitung rute tebas terpendek dan safety buffer tim MPA."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Right Column: Visual Mockup (60% width)
mockup_path = "samples/dashboard_mockup.png"
if os.path.exists(mockup_path):
    s5.shapes.add_picture(mockup_path, Inches(5.8), Inches(1.8), width=Inches(6.7), height=Inches(4.8))
else:
    add_card(s5, Inches(5.8), Inches(1.8), Inches(6.7), Inches(4.8), "MOCKUP DASBOR SMOKECUT", border_color=COLOR_AMBER)


# ==========================================================
# SLIDE 6: 04. PROPOSED SOLUTION (EKSEKUSI LAPANGAN)
# ==========================================================
s6 = prs.slides.add_slide(blank_slide_layout)
add_background(s6)
add_header(s6, "04. Proposed Solution (Eksekusi Lapangan)", "Dari Layar ke Lapangan: Aksi Cepat, Aman, & Sirkular")

steps = [
    ("1. Patroli Rutin", "Operator desa/BPBD menerbangkan drone standar 1–2 kali seminggu saat musim kering untuk mendata semak.", COLOR_SKY),
    ("2. Alert WhatsApp MPA", "Peta garis sekat bakar + estimasi panjang babatan + koordinat GPS terkirim otomatis ke grup WA MPA.", COLOR_AMBER),
    ("3. Peringatan Dini", "Pesan peringatan kualitas udara otomatis terkirim ke warga di zona arah angin (anjuran masker & tutup jendela).", COLOR_ROSE),
    ("4. Babat & Sirkular", "MPA membabat selebar 3–5 meter; rumput hasil babatan diangkut menjadi pakan ternak atau kompos desa.", COLOR_EMERALD)
]

w_box = Inches(2.75)
for idx, (title, desc, color) in enumerate(steps):
    left_pos = Inches(0.8 + idx * 2.95)
    add_card(s6, left_pos, Inches(1.8), w_box, Inches(4.8), border_color=color)

    tb = s6.shapes.add_textbox(left_pos + Inches(0.2), Inches(2.1), w_box - Inches(0.4), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.bold = True
    p1.font.size = Pt(19)
    p1.font.color.rgb = color
    p1.space_after = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 7: 05. IMPLEMENTATION PLAN (TIMELINE & MITRA)
# ==========================================================
s7 = prs.slides.add_slide(blank_slide_layout)
add_background(s7)
add_header(s7, "05. Implementation Plan", "Roadmap Pilot 6 Bulan & Kolaborasi Lintas Sektor")

# Top Container: 4 Phases Timeline
add_card(s7, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.4), "TIMELINE PILOT (2 DESA RAWAN KARHUTLA)", border_color=COLOR_SKY)
tb = s7.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(11.1), Inches(1.5))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Bulan 1 (Persiapan): MoU dengan BPBD & Desa, pemetaan baseline lahan, dan kalibrasi dataset lokal.\n• Bulan 2 (Integrasi & Pelatihan): Uji coba unggah video drone mitra + pelatihan pembabatan MPA.\n• Bulan 3–5 (Operasional): Patroli rutin pra-kemarau, pembuatan sekat bakar preventif, dan uji sistem WA.\n• Bulan 6 (Evaluasi & Skala): Audit penurunan kejadian api/asap dan penyusunan SOP replikasi kecamatan."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Bottom Container: 4 Key Partners
add_card(s7, Inches(0.8), Inches(4.4), Inches(11.7), Inches(2.2), "4 MITRA KOLABORASI KUNCI", border_color=COLOR_AMBER)
tb = s7.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(11.1), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• BPBD / Manggala Agni: Pemanfaatan aset drone dan validasi standar keselamatan sekat bakar.\n• Pemerintah Desa & MPA: Tim eksekutor pembabatan jalur dan pengolahan biomassa kompos.\n• Perguruan Tinggi / Akademisi: Mitra riset validasi model Computer Vision dan kalibrasi indeks VARI.\n• Sektor Swasta / CSR Perkebunan: Dukungan pendanaan berkelanjutan dan insentif desa tangguh."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 8: 05. IMPLEMENTATION PLAN (SUMBER DAYA & RISIKO)
# ==========================================================
s8 = prs.slides.add_slide(blank_slide_layout)
add_background(s8)
add_header(s8, "05. Implementation Plan", "Kebutuhan Sumber Daya Ramping & Mitigasi Risiko Lapangan")

# Left Column: Resources
add_card(s8, Inches(0.8), Inches(1.8), col_w, col_h, "KEBUTUHAN SUMBER DAYA RAMPING", border_color=COLOR_EMERALD)
tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.6), col_w - Inches(0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Hemat karena Tanpa Pengadaan Drone Baru:\nMemanfaatkan drone kamera RGB yang telah dimiliki BPBD atau jasa drone lokal.\n\n• Infrastruktur Komputasi Terjangkau:\nDapat dijalankan offline di laptop lapangan standar core i5 atau cloud server ringan.\n\n• Perlengkapan Keselamatan Lapangan:\nPaket APD dasar bagi tim MPA (masker respirator, sarung tangan tebal, sepatu bot, dan parang pemotong)."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Right Column: Risk Mitigation
add_card(s8, Inches(6.85), Inches(1.8), col_w, col_h, "MITIGASI RISIKO UTAMA", border_color=COLOR_ROSE)
tb = s8.shapes.add_textbox(Inches(7.1), Inches(2.6), col_w - Inches(0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. Susah Sinyal di Lapangan:\nAlur rekam–simpan–proses memastikan seluruh inferensi AI berjalan offline tanpa perlu internet.\n\n2. Keselamatan Tim Darat:\nAlgoritma mengunci safety buffer minimal (25–35 meter) searah angin agar MPA tidak mendekati kepala api.\n\n3. Salah Deteksi Kabut / Asap:\nSistem verifikasi cepat 1 klik oleh operator sebelum peringatan broadcast dipancarkan ke warga desa."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 9: 06. EXPECTED IMPACT & SUSTAINABILITY
# ==========================================================
s9 = prs.slides.add_slide(blank_slide_layout)
add_background(s9)
add_header(s9, "06. Expected Impact & Sustainability", "Dampak Terukur & Model Keberlanjutan Jangka Panjang")

# Top Container: KPI Impact
add_card(s9, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.5), "INDIKATOR KEBERHASILAN (PILOT 6 BULAN)", border_color=COLOR_SKY)
tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(11.1), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Output Terukur: 2 desa terpetakan penuh, ≥ 20 anggota MPA bersertifikat taktis, dan jalur sekat terbangun di 100% zona semak merah.\n• Outcome Perilaku: ≥ 80% pembabatan dilakukan preventif berbasis data peta; 100% biomassa hasil babatan diolah jadi kompos/pakan.\n• Impact Kualitas Udara: Penurunan luas lahan terbakar ≥ 50%, mencegah lonjakan partikulat PM2.5 masif ke kawasan permukiman."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE

# Bottom Container: Sustainability Model
add_card(s9, Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.1), "MODEL KEBERLANJUTAN (CROSS-SUBSIDY MODEL)", border_color=COLOR_EMERALD)
tb = s9.shapes.add_textbox(Inches(1.05), Inches(5.2), Inches(11.1), Inches(1.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Gratis 100% untuk Komunitas Desa & MPA: Didukung alokasi Dana Desa Tanggap Bencana.\n• Berbayar Ringan (SaaS / Program CSR): Dikenakan pada korporasi perkebunan dan dinas lingkungan daerah untuk mendanai pemeliharaan server dan ekspansi wilayah replikasi."
p.font.size = Pt(18)
p.font.color.rgb = COLOR_TEXT_WHITE


# ==========================================================
# SLIDE 10: CONCLUSION & REFERENCES
# ==========================================================
s10 = prs.slides.add_slide(blank_slide_layout)
add_background(s10)
add_header(s10, "Conclusion & References", "Kualitas Udara Bersih Dimulai dari Pencegahan Sebelum Asap Menyebar")

# Top Box: Conclusion Statement
add_card(s10, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.0), border_color=COLOR_SKY)
tb = s10.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "“SMOKECUT membuktikan bahwa solusi cerdas tidak harus mahal. Dengan memanfaatkan drone kamera RGB biasa dan algoritma visual terarah, kita mengubah paradigma pemadaman panik menjadi aksi preventif yang terukur, melindungi paru-paru warga secara berkelanjutan.”"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT_WHITE

# Bottom Box: References
add_card(s10, Inches(0.8), Inches(4.0), Inches(11.7), Inches(2.6), "REFERENSI KUNCI", border_color=COLOR_BORDER)
tb = s10.shapes.add_textbox(Inches(1.1), Inches(4.6), Inches(11.1), Inches(1.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. MarkPlus, Inc. (2025). Survei Persepsi dan Tindakan Masyarakat terhadap Kualitas Udara (Guidebook AIRIMPACT 2026).\n2. IQAir. (2026). Jabodetabek Air Quality Snapshot, 29 Oktober 2026.\n3. RCCC UI. (2023). Kajian Klaim BPJS Kesehatan Terkait Penyakit Polusi Udara di Jakarta.\n4. WHO. (2021). WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10).\n5. Gitelson, A. A., et al. (2002). Novel Algorithms for Remote Estimation of Vegetation Fraction (VARI). Remote Sensing of Environment."
p.font.size = Pt(13)
p.font.color.rgb = COLOR_TEXT_MUTED

# Save presentation
prs.save(OUTPUT_FILE)
print(f"Presentation successfully generated at: {OUTPUT_FILE}")
