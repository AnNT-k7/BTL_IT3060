# Quy trình thực hiện dự án xếp thời khóa biểu bằng AI

Tài liệu này chuyển [brief chi tiết](Brief_chi_tiet_xep_thoi_khoa_bieu_AI.md) thành các bước có thể thực hiện và kiểm tra. Phạm vi là một tuần học điển hình, dữ liệu mô phỏng, bộ giải CSP tự cài đặt và giao diện demo.

## 1. Sơ đồ công việc

```text
Xác định dữ liệu và quy tắc
          ↓
Kiểm tra đầu vào và kiểm tra lịch độc lập
          ↓
Sinh miền giá trị cho từng buổi học
          ↓
Quay lui cơ bản → MRV + forward checking
          ↓
Chấm điểm và cải thiện lịch hợp lệ
          ↓
CLI → giao diện web → xuất kết quả
          ↓
Thực nghiệm → báo cáo → demo
```

Mỗi bước chỉ được xem là hoàn thành khi **đầu ra và tiêu chí kiểm tra** bên dưới đã đạt. Bộ kiểm tra lịch độc lập được xây trước bộ giải để tránh việc thuật toán tự xác nhận kết quả sai của chính nó.

## 2. Bước 1 — Chuẩn bị môi trường và cấu trúc mã

**Đầu vào:** brief và Python. **Việc làm:** tạo thư mục dự án riêng, README, khai báo phụ thuộc, lệnh chạy từ terminal và cấu trúc thư mục `timetable_ai/`, `data/`, `tests/`. Chốt định dạng ngày/tiết, quy ước ID và trạng thái kết quả.

**Đầu ra:** có thể cài phụ thuộc, chạy `python -m timetable_ai --help` và xem dữ liệu mẫu. **Điều kiện qua bước:** người khác làm lại được trên máy mới chỉ từ README.

## 3. Bước 2 — Thiết kế dữ liệu và bộ kiểm tra

Tạo các thực thể **buổi học, phòng, giờ rảnh giảng viên, giờ ưu tiên và cấu hình tuần**. Mỗi buổi có ID, mã môn, giảng viên, nhóm sinh viên, sĩ số, số tiết liên tiếp và loại phòng. Nạp CSV/JSON, kiểm tra thiếu cột, mã trùng, tham chiếu sai, sĩ số/sức chứa âm, thời lượng nằm ngoài giới hạn, giờ không hợp lệ.

Viết `validate_schedule`: kiểm tra mỗi buổi được xếp đúng một lần, đúng phòng và loại phòng, giảng viên rảnh trong toàn bộ buổi; hai buổi không trùng phòng/giảng viên/nhóm sinh viên khi thời gian giao nhau. Hàm trả danh sách lỗi có loại và buổi liên quan, dùng lại cho CLI, web và thực nghiệm.

**Đầu ra:** dữ liệu hợp lệ được nạp thành mô hình thống nhất; dữ liệu lỗi bị từ chối với chỉ dẫn rõ. **Điều kiện qua bước:** các ca cố ý trùng phòng, giảng viên, nhóm, thiếu buổi, phòng nhỏ đều bị phát hiện.

## 4. Bước 3 — Mô hình CSP và quay lui cơ bản

Với mỗi buổi `S_i`, tạo biến `X_i`. Sinh miền `(ngày, tiết bắt đầu, phòng)` hợp lệ theo ràng buộc một buổi: không vượt giờ, phòng đủ chỗ/đúng loại, giảng viên rảnh mọi tiết của buổi. Khi gán `X_i`, kiểm tra xung đột với các biến đã gán; nếu không còn lựa chọn thì quay lui.

Ghi số nút đã xét, số lần quay lui, thời gian chạy và trạng thái `FEASIBLE`, `UNSAT` hoặc `TIMEOUT`. `UNSAT` chỉ được trả khi tìm kiếm đã duyệt hết; hết thời gian phải trả `TIMEOUT` ngay cả khi chưa thấy nghiệm.

**Đầu ra:** lệnh CLI xếp được lịch nhỏ. **Điều kiện qua bước:** lịch trả về qua bộ kiểm tra độc lập và có 0 lỗi cứng; bộ vô nghiệm nhỏ không bị báo nhầm là hết giờ.

## 5. Bước 4 — MRV và forward checking

Thêm chiến lược chọn buổi có ít giá trị khả dụng nhất (MRV), phá hòa bằng số buổi liên quan còn chưa xếp. Sau mỗi lần gán, forward checking loại giá trị xung đột ở các biến liên quan; nếu có miền rỗng, quay lui sớm. Lưu chính xác các giá trị đã xóa để khôi phục khi quay lui. Giữ quay lui cơ bản làm mốc so sánh.

**Đầu ra:** cùng bộ dữ liệu chạy được bằng cả hai chế độ. **Điều kiện qua bước:** hai chế độ cho kết quả hợp lệ; ca “miền rỗng” và ca “khôi phục miền” có kiểm thử riêng; thống kê nút và thời gian được ghi nhất quán.

## 6. Bước 5 — Chất lượng lịch và tìm kiếm cục bộ

Tính ba thành phần điểm phạt: tiết muộn, tiết trống giữa hai buổi trong ngày của cùng nhóm, giờ không đúng ưu tiên giảng viên. Chỉ chấm lịch hợp lệ. Thử chuyển một buổi sang giá trị khác hoặc hoán đổi hai buổi; chỉ giữ thay đổi không làm sai ràng buộc cứng và giảm điểm phạt. Ghi kết quả trước/sau tối ưu riêng.

**Đầu ra:** điểm phạt có giải thích và lịch sau cải thiện. **Điều kiện qua bước:** điểm sau không cao hơn điểm trước; lịch sau vẫn qua bộ kiểm tra độc lập. Nếu hết hạn thời gian, giữ lịch hợp lệ tốt nhất đã tìm thấy.

## 7. Bước 6 — Giao diện và kịch bản demo

Tạo ứng dụng Streamlit với ba khu vực: **dữ liệu**, **chạy thuật toán**, **kết quả**. Có bộ dữ liệu mẫu để mở ứng dụng là thử được; hỗ trợ tải CSV, chọn thuật toán, thời gian tối đa, trọng số, xem lưới lịch và thống kê, tải CSV kết quả. Khi đầu vào sai, giao diện hiển thị lỗi cụ thể và không chạy solver. Khi hết giờ hoặc vô nghiệm, dùng thông điệp khác nhau.

**Đầu ra:** demo nhập → giải → xem → xuất. **Điều kiện qua bước:** thay đổi một giờ rảnh của giảng viên rồi chạy lại cho kết quả mới hoặc thông báo đúng trạng thái; tệp xuất nạp lại và kiểm tra được.

## 8. Bước 7 — Dữ liệu thử nghiệm và phân tích

Tạo các bộ nhỏ, vừa, lớn bằng seed lưu trong dữ liệu; có bộ hợp lệ đã biết và bộ vô nghiệm có chủ đích. Chạy hai thuật toán trên **cùng input, máy, cấu hình và giới hạn thời gian**. Lưu CSV kết quả: trạng thái, thời gian, số nút, số lần quay lui, điểm phạt, số lỗi cứng. Không dùng một trường hợp duy nhất để kết luận thuật toán nào tốt hơn.

**Đầu ra:** bảng thực nghiệm và biểu đồ hoặc bảng so sánh trong báo cáo. **Điều kiện qua bước:** người khác chạy lại lệnh thực nghiệm và tái tạo được bảng; nhận xét dựa trên số đo thực tế, kể cả khi heuristic có trường hợp chậm hơn.

## 9. Bước 8 — Báo cáo, slide và bàn giao

Báo cáo nêu bài toán, biểu diễn CSP, các ràng buộc, thuật toán và mã giả, thiết kế dữ liệu, thực nghiệm, hình ảnh demo, phần nhóm tự làm và nguồn mã tham khảo. Slide tập trung vào một ví dụ thay đổi ràng buộc, các bước MRV/forward checking và số liệu so sánh. README ghi lệnh cài, chạy CLI/web/thực nghiệm, cấu trúc dữ liệu và cách tái lập kết quả.

**Đầu ra bàn giao:** mã nguồn, dữ liệu mẫu, kiểm thử, README, ứng dụng chạy được, báo cáo/slide và PDF báo cáo tiến độ. PDF tiến độ phải phản ánh đúng phần đã hoàn thành và phần còn tiếp theo tại thời điểm tạo.

## 10. Thứ tự ưu tiên nếu thời gian hạn chế

1. Mô hình dữ liệu, bộ kiểm tra độc lập, quay lui cơ bản và MRV + forward checking.
2. CLI và dữ liệu mẫu chạy được, thực nghiệm so sánh có số liệu thật.
3. Giao diện web đủ cho demo và xuất CSV.
4. Tìm kiếm cục bộ, biểu đồ nâng cao, so sánh với thư viện OR-Tools.

Mọi chức năng mở rộng phải giữ được quy tắc: **chỉ công bố lịch khi bộ kiểm tra độc lập xác nhận không có vi phạm cứng**.

## 11. Đối chiếu tiến độ thực tế (16/10/2026)

| Bước | Trạng thái | Minh chứng |
| --- | --- | --- |
| 1–2. Môi trường, dữ liệu, kiểm tra | Đã thực hiện | `du_an_xep_thoi_khoa_bieu/README.md`, `data/`, `timetable_ai/core.py` |
| 3–4. Hai bộ giải CSP | Đã thực hiện | CLI, 15 kiểm thử tự động, bộ `backtracking` và `tight_demo` |
| 5. Điểm phạt và tìm kiếm cục bộ | Đã thực hiện | Chuyển buổi/hoán đổi hợp lệ, kiểm thử điểm sau không tăng |
| 6. Giao diện demo | Đã thực hiện | `app.py`, chạy thử luồng mở demo → đổi giờ rảnh → xếp lại bằng AppTest |
| 7. Thực nghiệm | Đã thực hiện trên dữ liệu mô phỏng | `results/benchmark.csv` có 170 phép đo, 5 bộ khả thi và 2 ca tập trung |
| 8. Báo cáo và bàn giao | Có bản thảo | `Bao_cao_ky_thuat.pdf`, `Slide_thuyet_trinh.pdf`, `Bao_cao_tien_do_du_an.pdf`; cần bổ sung thông tin nhóm và xác nhận yêu cầu trình bày từ giảng viên |

Các số liệu trong báo cáo là kết quả của lần chạy đã lưu trong CSV. Chạy lại trên máy khác có thể cho thời gian khác; trạng thái nghiệm, số nút và số lần quay lui vẫn có thể tái kiểm tra bằng các lệnh trong README.
