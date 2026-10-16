# BTL IT3060: Xếp thời khóa biểu bằng trí tuệ nhân tạo

Dự án bài tập lớn môn Nhập môn trí tuệ nhân tạo. Ứng dụng xây dựng thời khóa biểu từ dữ liệu buổi học, phòng học và giờ rảnh giảng viên bằng bài toán thỏa mãn ràng buộc (CSP). Dữ liệu đi kèm là dữ liệu mô phỏng.

## Chạy ứng dụng

Cần Python 3.10 trở lên. Mở terminal tại thư mục `du_an_xep_thoi_khoa_bieu`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install streamlit==1.66.0
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Nếu máy không nhận lệnh `py`, dùng `python` ở dòng đầu. Mở `http://localhost:8501` nếu trình duyệt không tự bật. Trong giao diện, chọn dữ liệu demo rồi bấm **Xếp lịch**. Cài riêng Streamlit là đủ để chạy ứng dụng; các thư viện còn lại trong `requirements.txt` dùng để tạo lại PDF.

### Linux / WSL

```bash
python3 -m venv .venv
.venv/bin/python -m pip install streamlit==1.66.0
.venv/bin/python -m streamlit run app.py
```

## Kiểm tra thuật toán

Trong thư mục `du_an_xep_thoi_khoa_bieu`:

```bash
python3 -m unittest discover -s tests -v
python3 -m timetable_ai solve --data data/demo --solver enhanced
```

Trên Windows, thay `python3` bằng `.\.venv\Scripts\python.exe` nếu đã tạo môi trường như trên.

## Tài liệu

- [Ý tưởng đề tài](Y_tuong_bai_tap_lon_AI.md)
- [Brief chi tiết](Brief_chi_tiet_xep_thoi_khoa_bieu_AI.md)
- [Quy trình thực hiện](Quy_trinh_thuc_hien_du_an.md)
- [Báo cáo tiến độ PDF](Bao_cao_tien_do_du_an.pdf)
- [Báo cáo kỹ thuật PDF](Bao_cao_ky_thuat.pdf)
- [Slide thuyết trình PDF](Slide_thuyet_trinh.pdf)
- [Hướng dẫn chi tiết, định dạng dữ liệu và giới hạn](du_an_xep_thoi_khoa_bieu/README.md)

Mã nguồn, dữ liệu mô phỏng, kết quả thực nghiệm và bộ kiểm thử nằm trong [`du_an_xep_thoi_khoa_bieu/`](du_an_xep_thoi_khoa_bieu/). Các PDF đã tạo sẵn; trên Windows không cần chạy script tạo PDF để xem báo cáo.
