"""Build a Vietnamese, evidence-based progress PDF for the lecturer."""

from __future__ import annotations

import csv
import datetime
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).parent
OUTPUT = ROOT.parent / 'Bao_cao_tien_do_du_an.pdf'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')


def register_fonts() -> None:
    regular = FONT_DIR / 'DejaVuSans.ttf'
    bold = FONT_DIR / 'DejaVuSans-Bold.ttf'
    if not regular.exists() or not bold.exists():
        raise RuntimeError('Cần font DejaVu Sans để tạo PDF tiếng Việt')
    pdfmetrics.registerFont(TTFont('DejaVu', str(regular)))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(bold)))
    pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold')


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def main() -> None:
    check = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                           cwd=ROOT, capture_output=True, text=True)
    if check.returncode:
        raise RuntimeError('Kiểm thử chưa đạt; không tạo báo cáo tiến độ:\n' + check.stderr)
    tests = sum(' ... ok' in line for line in check.stderr.splitlines())
    rows = list(csv.DictReader((ROOT / 'results' / 'benchmark.csv').open(encoding='utf-8')))
    if len(rows) != 170:
        raise RuntimeError('Cần chạy python3 run_experiments.py trước khi tạo PDF')
    by_case = defaultdict(list)
    for row in rows:
        by_case[(row['case'], row['solver'])].append(row)
        expected = 'UNSAT' if row['case'] == 'unsat' else 'FEASIBLE'
        if row['status'] != expected or (expected == 'FEASIBLE' and row['hard_violations'] != '0'):
            raise RuntimeError('Thực nghiệm có trạng thái hoặc lịch không đúng')

    register_fonts()
    source_platform = rows[0]['platform']
    environment = 'WSL2' if 'microsoft' in source_platform.lower() else source_platform
    styles = getSampleStyleSheet()
    title = ParagraphStyle('TitleVN', parent=styles['Title'], fontName='DejaVu-Bold',
                           fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=7)
    h1 = ParagraphStyle('H1VN', parent=styles['Heading2'], fontName='DejaVu-Bold',
                        fontSize=10, leading=13, spaceBefore=7, spaceAfter=3)
    body = ParagraphStyle('BodyVN', parent=styles['BodyText'], fontName='DejaVu',
                          fontSize=8.5, leading=12, spaceAfter=3)
    small = ParagraphStyle('SmallVN', parent=body, fontSize=7.5, leading=10)
    table_header = ParagraphStyle('TableHeadVN', parent=small, fontName='DejaVu-Bold')
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                            topMargin=13 * mm, bottomMargin=13 * mm)
    story = [p('BÁO CÁO TIẾN ĐỘ BÀI TẬP LỚN', title),
             p(f'<b>Học phần:</b> Nhập môn trí tuệ nhân tạo<br/><b>Đề tài:</b> Hệ thống xếp thời khóa biểu học phần bằng bài toán CSP<br/><b>Ngày báo cáo:</b> {datetime.date.today():%d/%m/%Y}', body)]

    story += [p('1. Mục tiêu và phạm vi', h1),
              p('Xây dựng ứng dụng xếp lịch một tuần học điển hình cho các buổi học, phòng, giảng viên và nhóm sinh viên. Trọng tâm là tự cài đặt quay lui cơ bản và phiên bản dùng MRV + forward checking; sau đó so sánh trên cùng bộ dữ liệu. Dữ liệu đang dùng là dữ liệu mô phỏng, không phải lịch chính thức của trường.', body),
              p('2. Công việc đã hoàn thành', h1)]
    completed = [
        'Định nghĩa dữ liệu CSV/JSON, kiểm tra tham chiếu, sức chứa phòng, loại phòng, thời lượng và giờ rảnh.',
        'Cài bộ kiểm tra lịch độc lập: phát hiện thiếu buổi, trùng phòng, giảng viên, nhóm và sai điều kiện một buổi.',
        'Cài hai bộ giải CSP: quay lui cơ bản và quay lui với MRV, degree heuristic, forward checking; phân biệt FEASIBLE, UNSAT, TIMEOUT.',
        'Cài điểm phạt (tiết muộn, tiết trống, giờ không ưa thích) và tìm kiếm cục bộ chỉ giữ lịch hợp lệ có điểm thấp hơn.',
        'Tạo CLI, giao diện Streamlit, lưới lịch theo phòng/giảng viên/nhóm, thay đổi giờ rảnh trong phiên, xuất và nạp lại CSV.',
        f'Tạo dữ liệu mẫu, script sinh dữ liệu có seed, script thực nghiệm; {tests}/{tests} kiểm thử tự động đạt.',
    ]
    story.extend(p(f'• {line}', body) for line in completed)
    story += [p('3. Kết quả thực nghiệm bước đầu', h1),
              p(f'Đo trên Python {rows[0]["python_version"]}, {environment}, cùng giới hạn 10 giây cho mỗi lần chạy. Năm bộ dữ liệu khả thi có 3 seed (3161–3163), mỗi seed lặp 5 lần với cả hai bộ giải. Bảng dưới là trung bình của 15 lần/thuật toán ở ba quy mô thông thường; cả 150 lịch khả thi đều có 0 vi phạm cứng.', body)]
    table_data = [[p(x, table_header) for x in ('Quy mô', 'Bộ giải', 'Thời gian (ms)', 'Nút xét', 'Điểm phạt')]]
    for case, display in (('small', 'Nhỏ (9 buổi)'), ('medium', 'Vừa (24 buổi)'), ('large', 'Lớn (40 buổi)')):
        for solver, label in (('baseline', 'Quay lui'), ('enhanced', 'MRV + FC')):
            items = by_case[(case, solver)]
            time_ms = statistics.mean(float(row['elapsed_seconds']) for row in items) * 1000
            nodes = statistics.mean(int(row['nodes']) for row in items)
            cost = statistics.mean(float(row['score']) for row in items)
            table_data.append([p(display, small), p(label, small), p(f'{time_ms:.2f}', small),
                               p(f'{nodes:.1f}', small), p(f'{cost:.1f}', small)])
    table = Table(table_data, colWidths=[36 * mm, 34 * mm, 34 * mm, 28 * mm, 27 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dce9f3')),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#aab7c4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story += [table, Spacer(1, 2 * mm),
              p('Trong dữ liệu thông thường, MRV + forward checking xét ít nút hơn nhưng chạy lâu hơn vì chi phí cập nhật miền; cả hai bộ giải đều không phải quay lui. Với 20/40 buổi ràng buộc chặt, bản cơ bản quay lui trung bình 17,7/32,3 lần, bản cải tiến không quay lui; bản cải tiến vẫn chậm hơn ở phép đo thời gian này. Vì vậy chưa thể kết luận heuristic luôn nhanh hơn.', body),
              p(f'Bộ dữ liệu cố ý vô nghiệm được cả hai bộ giải báo UNSAT sau khi duyệt hết; quay lui cơ bản xét trung bình {statistics.mean(int(r["nodes"]) for r in by_case[("unsat", "baseline")]):.0f} nút, bản cải tiến xét {statistics.mean(int(r["nodes"]) for r in by_case[("unsat", "enhanced")]):.0f} nút. Kiểm thử với thời hạn 0 giây báo TIMEOUT, không gắn nhãn vô nghiệm. Giao diện web đã được chạy thử bằng Streamlit và AppTest, không phát sinh lỗi ở luồng mở demo → xếp lịch.', body),
              p('4. Phần còn cần tiếp tục', h1),
              p('Thử thêm dữ liệu gần lịch thật hơn, có phòng dùng chung và giảng viên dạy nhiều nhóm; rà soát bản thảo báo cáo học thuật và slide trước khi nộp; xin ý kiến giảng viên về phạm vi dữ liệu mô phỏng và hình thức nộp. Phần giải thích vô nghiệm hiện chỉ là dấu vết miền bị rỗng, chưa phải tập nguyên nhân tối thiểu.', body),
              p('5. Tệp minh chứng', h1),
              p('Mã nguồn, dữ liệu, kiểm thử và hướng dẫn: <b>du_an_xep_thoi_khoa_bieu/</b>. Kết quả đo gốc: <b>results/benchmark.csv</b>. Báo cáo kỹ thuật và slide đã xuất PDF trong thư mục tài liệu này. Quy trình: <b>Quy_trinh_thuc_hien_du_an.md</b>.', body)]

    def footer(canvas, document):
        canvas.setFont('DejaVu', 8)
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f'Trang {document.page}')

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'Created {OUTPUT} ({OUTPUT.stat().st_size} bytes); {tests} tests passed.')


if __name__ == '__main__':
    main()
