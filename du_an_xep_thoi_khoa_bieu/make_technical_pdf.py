"""Render the technical Markdown report as a paginated PDF."""

from __future__ import annotations

import re
from pathlib import Path

import markdown
from weasyprint import HTML


ROOT = Path(__file__).parent
SOURCE = ROOT / 'Bao_cao_ky_thuat.md'
OUTPUT = ROOT.parent / 'Bao_cao_ky_thuat.pdf'

CSS = """
@page {
  size: A4;
  margin: 17mm 18mm 19mm 18mm;
  @bottom-right { content: 'Trang ' counter(page); font: 8pt 'DejaVu Sans'; color: #64748b; }
}
body { font-family: 'DejaVu Sans', sans-serif; color: #1f2937; font-size: 9.3pt; line-height: 1.48; }
h1 { color: #102a43; font-size: 17pt; line-height: 1.25; margin: 0 0 10pt; }
h2 { color: #0f766e; font-size: 12pt; margin: 15pt 0 5pt; break-after: avoid; }
h3 { color: #102a43; font-size: 10.5pt; margin: 11pt 0 4pt; break-after: avoid; }
p { margin: 4pt 0 7pt; orphans: 3; widows: 3; }
ul, ol { margin: 4pt 0 7pt; padding-left: 18pt; }
li { margin: 2pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.2pt; margin: 8pt 0 10pt; }
th, td { border: 0.5pt solid #cbd5e1; padding: 4pt 5pt; vertical-align: top; }
th { background: #dce9f3; color: #102a43; }
tr { break-inside: avoid; }
pre { background: #f1f5f9; border-left: 3pt solid #0d9488; padding: 7pt; font-size: 8pt;
      white-space: pre-wrap; break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.92em; }
a { color: #0f766e; text-decoration: none; }
"""


def main() -> None:
    source = SOURCE.read_text(encoding='utf-8')
    source = re.sub(r'^---\n.*?\n---\n', '', source, count=1, flags=re.S)
    html_body = markdown.markdown(source, extensions=['tables', 'fenced_code'])
    html = f'<!doctype html><html lang="vi"><meta charset="utf-8"><style>{CSS}</style><body>{html_body}</body></html>'
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(OUTPUT))
    print(f'Created {OUTPUT} ({OUTPUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
