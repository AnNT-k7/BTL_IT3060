"""Render Slide_thuyet_trinh.md to a compact presentation PDF."""

from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).parent
OUTPUT = ROOT.parent / 'Slide_thuyet_trinh.pdf'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
PAGE_W, PAGE_H = 960, 540


def main() -> None:
    pdfmetrics.registerFont(TTFont('DejaVu', str(FONT_DIR / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(FONT_DIR / 'DejaVuSans-Bold.ttf')))
    chunks = (ROOT / 'Slide_thuyet_trinh.md').read_text(encoding='utf-8').split('\n---\n')
    slides = []
    for chunk in chunks:
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        if not lines or not lines[0].startswith('# '):
            raise ValueError('Mỗi slide phải bắt đầu bằng tiêu đề #')
        slides.append((lines[0][2:], lines[1:]))
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
    pdf.setTitle('Xếp thời khóa biểu học phần bằng CSP')
    body_style = ParagraphStyle('slide-body', fontName='DejaVu', fontSize=20, leading=30,
                                textColor=colors.HexColor('#243447'))
    for index, (title, lines) in enumerate(slides, 1):
        pdf.setFillColor(colors.HexColor('#f7fafc'))
        pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor('#0d9488'))
        pdf.rect(0, PAGE_H - 12, PAGE_W, 12, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor('#102a43'))
        pdf.setFont('DejaVu-Bold', 30 if index > 1 else 35)
        pdf.drawString(64, PAGE_H - 88, title)
        y = PAGE_H - 138
        for line in lines:
            bullet = line.startswith('- ')
            if bullet:
                pdf.setFillColor(colors.HexColor('#0d9488'))
                pdf.circle(77, y - 9, 5, fill=1, stroke=0)
                line = line[2:]
            paragraph = Paragraph(escape(line), body_style)
            width = 790 if bullet else 830
            _, height = paragraph.wrap(width, PAGE_H)
            paragraph.drawOn(pdf, 95 if bullet else 64, y - height)
            y -= height + (20 if bullet else 25)
        if y < 40:
            raise ValueError(f'Slide {index} quá dài; rút ngắn nội dung')
        pdf.setStrokeColor(colors.HexColor('#cbd5e1'))
        pdf.line(64, 44, PAGE_W - 64, 44)
        pdf.setFont('DejaVu', 11)
        pdf.setFillColor(colors.HexColor('#64748b'))
        pdf.drawString(64, 25, 'Nhập môn trí tuệ nhân tạo • Dữ liệu mô phỏng')
        pdf.drawRightString(PAGE_W - 64, 25, f'{index} / {len(slides)}')
        pdf.showPage()
    pdf.save()
    print(f'Created {OUTPUT}: {len(slides)} slides')


if __name__ == '__main__':
    main()
