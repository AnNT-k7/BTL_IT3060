# Xếp thời khóa biểu học phần bằng CSP

Ứng dụng demo cho môn **Nhập môn trí tuệ nhân tạo**. Hệ thống xếp một tuần học điển hình từ danh sách buổi học, phòng, giờ rảnh giảng viên và các ưu tiên. Dữ liệu trong `data/` là **mô phỏng**, không phải thời khóa biểu chính thức của trường.

## Chạy nhanh

Đã thử với Python 3.14.4. Từ thư mục `du_an_xep_thoi_khoa_bieu`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m timetable_ai solve --data data/demo --solver enhanced --output schedule.csv
streamlit run app.py
```

Trên Windows, kích hoạt môi trường bằng `.venv\Scripts\activate` và có thể dùng `python` thay cho `python3`. Nếu chỉ chạy thuật toán và kiểm thử, không cần cài thư viện ngoài.

Một cách chạy giao diện với `uv`:

```bash
uv run --with streamlit==1.66.0 streamlit run app.py
```

## Các lệnh chính

```bash
python3 -m timetable_ai --help
python3 -m timetable_ai solve --data data/demo --solver baseline
python3 -m timetable_ai solve --data data/demo --solver enhanced --output schedule.csv
python3 -m timetable_ai benchmark --data data/backtracking
python3 run_experiments.py
python3 -m unittest discover -s tests -v
python3 make_progress_pdf.py
python3 make_technical_pdf.py
python3 make_slides_pdf.py
```

`run_experiments.py` tái tạo 5 bộ khả thi (`small`, `medium`, `large`, `tight20`, `tight40`) × 3 seed × 2 thuật toán × 5 lần lặp, cùng 2 ca tập trung (`backtracking`, `unsat`) × 2 thuật toán × 5 lần lặp; tổng cộng **170 phép đo** trong `results/benchmark.csv`. `generate_data.py` tạo lại các bộ mẫu `small`, `demo`, `large`, `tight_demo`, `unsat`. Các bộ `tight` có nghiệm cài sẵn và giờ dạy hạn chế để đo tác dụng của MRV; mỗi nhóm bốn buổi dùng một loại phòng riêng. Đây là stress test có kiểm soát, chưa đại diện cho lịch thật. Mọi phép đo thời gian phụ thuộc máy chạy; không dùng một kết quả đơn lẻ để khẳng định thuật toán luôn nhanh hơn.

Hai script tạo PDF dùng font **DejaVu Sans** ở `/usr/share/fonts/truetype/dejavu`. Các PDF đã được tạo sẵn trong thư mục cha; nếu chạy lại trên hệ điều hành khác, sửa đường dẫn font trong script cho phù hợp.

Lệnh `solve` trả mã thoát `0` khi có lịch, `3` khi đã chứng minh vô nghiệm, `4` khi hết thời gian, `2` khi dữ liệu/lựa chọn không hợp lệ.

## Luồng giao diện

1. Chạy `streamlit run app.py`; dùng dữ liệu demo hoặc tải cùng lúc `sessions.csv`, `rooms.csv`, `availability.csv`, `config.json` và tùy chọn `preferences.csv`.
2. Trong phần **Thử thay đổi giờ rảnh**, chọn giảng viên, ngày, tiết và bật/tắt quyền dạy. Thay đổi được giữ trong phiên giao diện hiện tại.
3. Chọn `enhanced` (MRV + forward checking) hoặc `baseline`, giới hạn thời gian và trọng số ưu tiên; bấm **Xếp lịch**.
4. Xem trạng thái, thống kê, lưới tuần theo nhóm/giảng viên/phòng, điểm phạt; thử một khung giờ đề xuất để xem lý do xung đột; tải `schedule.csv`.

Trạng thái `UNSAT` nghĩa là bộ giải đã xét hết các khả năng mà không có lịch; `TIMEOUT` chỉ nghĩa là chưa tìm thấy trong thời gian cho phép. Giao diện hiển thị tối đa 20 dòng dấu vết tìm kiếm để minh họa cách chọn biến và xóa miền, chưa cung cấp tập nguyên nhân vô nghiệm tối thiểu.

## Định dạng dữ liệu

| Tệp | Cột/khóa bắt buộc | Ghi chú |
| --- | --- | --- |
| `sessions.csv` | `session_id,course_id,teacher_id,group_id,size,duration,room_type` | `duration` là 1 hoặc 2 tiết; `room_type` để trống nghĩa là bất kỳ |
| `rooms.csv` | `room_id,capacity,room_type` | Phòng phải chứa đủ `size` |
| `availability.csv` | `teacher_id,day,period,available` | Giờ không khai báo mặc định là không rảnh; `available` là `true/false` hoặc `1/0` |
| `preferences.csv` | `teacher_id,day,period,preference` | Tùy chọn; số nguyên từ 0 đến 1.000.000, 0 là ưu tiên nhất |
| `config.json` | `days,periods_per_day` | Tùy chọn: `weights`, `time_limit_seconds` |

Lịch xuất có các cột `session_id,day,start_period,room_id`. Hàm `import_csv` nạp lịch xuất; dùng `validate_schedule` để xác thực sau khi nạp. Bộ kiểm tra này độc lập với bộ giải và chặn xuất lịch có xung đột.

## Thuật toán và cấu trúc

- `timetable_ai/core.py`: đọc/kiểm tra dữ liệu, tạo miền `(ngày, tiết bắt đầu, phòng)`, kiểm tra xung đột, quay lui cơ bản, MRV + degree + forward checking, điểm phạt và tìm kiếm cục bộ.
- `timetable_ai/__main__.py`: giao diện dòng lệnh.
- `app.py`: giao diện Streamlit.
- `generate_data.py`: sinh dữ liệu mô phỏng với seed cố định.
- `run_experiments.py`: đo hai thuật toán trên cùng tập dữ liệu và giới hạn 10 giây.
- `tests/`: kiểm tra xung đột, dữ liệu lỗi, UNSAT/TIMEOUT, vòng xuất–nạp và tính hợp lệ sau tối ưu.
- `Bao_cao_ky_thuat.md`: bản thảo báo cáo học thuật với mô hình, phương pháp, số liệu và giới hạn.
- `make_technical_pdf.py`: xuất báo cáo học thuật thành `../Bao_cao_ky_thuat.pdf`.
- `Slide_thuyet_trinh.md`: nội dung 8 slide; `make_slides_pdf.py` tạo `../Slide_thuyet_trinh.pdf`.

Điểm phạt là tổng có trọng số của **tiết muộn**, **tiết trống của nhóm trong cùng ngày**, **giờ không ưa thích**. Bộ giải CSP tìm nghiệm hợp lệ đầu tiên; nếu bật **Cải thiện điểm phạt**, tìm kiếm cục bộ thử chuyển từng buổi sang khung khác hoặc hoán đổi hai buổi, và chỉ giữ thay đổi vừa hợp lệ vừa giảm điểm. Điểm trước/sau được hiển thị riêng. Thời gian tìm lịch và thời gian tối ưu cục bộ là hai giới hạn riêng trong giao diện.

## Nguồn tham khảo và phần tự xây dựng

- [AIMA Python, `csp.py`](https://github.com/aimacode/aima-python/blob/master/aima/csp.py) — tham khảo cách biểu diễn CSP, MRV và forward checking; repository dùng [MIT](https://github.com/aimacode/aima-python/blob/master/LICENSE).
- [Google OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver) — tài liệu đối chiếu cách mô hình hóa ràng buộc, không được dùng làm bộ giải của dự án này.

Mã nguồn trong thư mục này được viết riêng cho bài toán thời khóa biểu; không sao chép module `csp.py` hoặc dùng OR-Tools để giải. Nếu bổ sung mã từ nguồn ngoài về sau, cần ghi nguồn, giấy phép và phần thay đổi trong README/báo cáo.

## Giới hạn hiện tại

Ứng dụng chưa xử lý tuần chẵn/lẻ, xếp giảng viên tự động, lớp ghép hoặc đăng ký học phần theo từng sinh viên. Demo dùng dữ liệu mô phỏng và chưa được kiểm thử trên dữ liệu vận hành thực tế. Bộ dữ liệu thông thường còn khá dễ: ở 3 seed hiện tại cả hai bộ giải đều tìm lịch mà không phải quay lui. Bộ `tight` tạo thêm trường hợp quay lui ở quy mô 20–40 buổi, nhưng các phòng được tách theo loại nên vẫn là bài toán có cấu trúc nhân tạo. Thời gian giải bằng MRV + forward checking có thể cao hơn quay lui cơ bản do phải cập nhật miền sau mỗi phép gán. Dấu vết trên giao diện cho ví dụ lý do loại giá trị, không phải lời giải thích tối thiểu cho một bài toán vô nghiệm.
