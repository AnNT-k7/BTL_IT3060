# Bản thảo ý tưởng bài tập lớn: Hệ thống xếp thời khóa biểu học phần thông minh

## 1. Tóm tắt đề tài

Xây dựng một ứng dụng hỗ trợ xếp thời khóa biểu cho một nhóm lớp học phần trong một học kỳ. Người dùng nhập danh sách buổi học, giảng viên, nhóm sinh viên, phòng học và các khung giờ khả dụng. Hệ thống tự tìm lịch hợp lệ, hạn chế các giờ học không mong muốn và giải thích vì sao một buổi học không thể được xếp vào một khung giờ cụ thể.

Trọng tâm nghiên cứu là **bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problem — CSP)** và **tìm kiếm có sử dụng tri thức**. Đây là các nội dung có trong tài liệu môn học, đặc biệt là bài giảng *L6 — Thỏa mãn ràng buộc* (quay lui, MRV, forward checking) và *L4 — Tìm kiếm với tri thức bổ sung*. Sản phẩm cho phép quan sát hiệu quả của từng chiến lược trên cùng một bộ dữ liệu, thay vì chỉ hiển thị thời khóa biểu cuối cùng.

## 2. Bài toán và giá trị sử dụng

Việc xếp lịch thủ công dễ gặp xung đột: một giảng viên hoặc phòng học bị đặt ở hai nơi cùng lúc, lớp quá đông so với sức chứa phòng, hoặc một nhóm sinh viên có hai môn trùng giờ. Khi dữ liệu thay đổi, người xếp lịch phải kiểm tra lại nhiều buổi học.

Ứng dụng hướng đến người phụ trách lập lịch cho một khoa hoặc một tập lớp quy mô nhỏ. Sản phẩm dự kiến cho phép:

- Nhập hoặc tải lên dữ liệu từ CSV, kiểm tra lỗi dữ liệu đầu vào.
- Sinh một thời khóa biểu thỏa các ràng buộc bắt buộc.
- Chọn các mức ưu tiên như tránh tiết quá muộn, giảm khoảng trống trong ngày, tôn trọng giờ dạy mong muốn.
- Xem lịch theo phòng, giảng viên và nhóm sinh viên; xuất CSV.
- Xem thống kê thời gian chạy, số nút tìm kiếm, số lần quay lui và điểm chất lượng lịch.
- Nhận thông báo có thể hiểu được khi bài toán vô nghiệm, ví dụ “giảng viên A không còn khung giờ phù hợp cho hai buổi còn lại”.

## 3. Mô hình trí tuệ nhân tạo

### Biểu diễn CSP

- **Biến:** mỗi buổi học cần xếp là một biến `X_i`.
- **Miền giá trị:** các bộ `(ngày, tiết bắt đầu, phòng)` khả thi cho buổi đó. Một buổi học có thể kéo dài 1–2 tiết liên tiếp; các lựa chọn vượt cuối ngày hoặc không đủ chỗ được loại từ đầu.
- **Tri thức/ràng buộc cứng:** mỗi buổi có đúng một vị trí; một phòng, một giảng viên và một nhóm sinh viên không được có các buổi học chồng thời gian; phòng đủ sức chứa; giảng viên chỉ dạy trong giờ khả dụng; buổi nhiều tiết phải liên tục và ở cùng phòng.
- **Ràng buộc mềm:** hạn chế học quá muộn, giảm tiết trống giữa các buổi trong ngày và ưu tiên khung giờ mong muốn. Mỗi loại có trọng số do người dùng cấu hình.

Lời giải trước hết phải thỏa **toàn bộ ràng buộc cứng**. Trong các lời giải hợp lệ, hệ thống chọn lịch có tổng điểm phạt thấp hơn. Điểm phạt và từng thành phần của nó được hiển thị công khai để người dùng hiểu lý do chọn lịch.

### Thuật toán chính

1. **Mốc so sánh:** quay lui cơ bản, xét biến và giá trị theo thứ tự cố định.
2. **Phiên bản cải tiến:** chọn biến theo *Minimum Remaining Values* (MRV); khi hòa, ưu tiên biến có nhiều quan hệ xung đột hơn; dùng *forward checking* để xóa sớm các giá trị không còn hợp lệ. Có thể thêm *Least Constraining Value* (LCV) nếu thời gian cho phép.
3. **Tối ưu lịch:** sau khi có một lời giải hợp lệ, thử hoán đổi hoặc chuyển buổi học sang vị trí khác để giảm điểm phạt, chỉ chấp nhận lịch vẫn thỏa ràng buộc cứng. Nếu dữ liệu lớn gây chậm, giới hạn thời gian chạy và trả về lịch hợp lệ tốt nhất đã tìm thấy.

MRV và forward checking cần được **tự cài đặt hoặc điều chỉnh rõ ràng**, có mã nguồn và ví dụ minh họa từng bước. Mục tiêu là chứng minh hiểu thuật toán; giao diện chỉ là lớp trình bày kết quả.

## 4. Sản phẩm và kịch bản trình diễn

Giao diện web gọn nhẹ bằng **Python + Streamlit**; dữ liệu lưu trong CSV/JSON. Ba màn hình chính:

1. **Dữ liệu và ràng buộc:** tải CSV mẫu hoặc chỉnh sửa danh sách buổi học, phòng, giảng viên, nhóm sinh viên, giờ khả dụng.
2. **Xếp lịch:** chọn thuật toán, đặt trọng số ưu tiên, chạy và xem tiến độ/thống kê.
3. **Kết quả:** xem thời khóa biểu dạng lưới, bộ lọc theo đối tượng, danh sách cảnh báo, điểm phạt và nút xuất dữ liệu.

**Demo đề xuất:** chạy dữ liệu mẫu; thêm một buổi học để tạo xung đột; xem hệ thống xếp lại lịch; khóa một khung giờ của giảng viên; chạy lại và quan sát thay đổi. Một bộ dữ liệu cố ý vô nghiệm sẽ dùng để trình diễn thông báo nguyên nhân.

## 5. Dữ liệu và phạm vi

Tạo bộ dữ liệu mô phỏng có chú thích nguồn gốc, không gắn với thời khóa biểu chính thức của trường. Quy mô khởi đầu: khoảng **20–40 buổi học, 5–8 phòng, 8–15 giảng viên, 5–10 nhóm sinh viên**, 5 ngày học và 6–8 tiết/ngày. Chuẩn bị ít nhất ba mức khó: dễ, trung bình, khó; mỗi mức có bản hợp lệ và một tình huống vô nghiệm có chủ đích.

Để đề tài vừa sức, phiên bản đầu chỉ xếp **một tuần học điển hình**; không xử lý lịch học thay đổi theo từng tuần, lớp ghép phức tạp hoặc đăng ký môn tự do của từng sinh viên. Có thể mở rộng nếu phần lõi và đánh giá đã hoàn chỉnh.

## 6. Đánh giá thực nghiệm

Chạy quay lui cơ bản và phiên bản cải tiến trên **cùng bộ dữ liệu, cùng máy và cùng giới hạn thời gian**. Ghi lại:

| Chỉ số | Ý nghĩa |
| --- | --- |
| Tỷ lệ tạo được lịch hợp lệ | Khả năng giải các bộ dữ liệu trong thời hạn |
| Số xung đột ràng buộc cứng | Phải bằng 0 đối với lịch được công bố |
| Thời gian chạy, số nút, số lần quay lui | Hiệu quả tìm kiếm |
| Tổng điểm phạt và từng thành phần | Chất lượng lịch theo ưu tiên đã đặt |
| Kết quả với dữ liệu vô nghiệm | Khả năng phát hiện và giải thích trường hợp không thể xếp |

Mỗi cấu hình được chạy nhiều lần với **seed cố định và được ghi lại** nếu có bước ngẫu nhiên. Báo cáo trình bày bảng số liệu, biểu đồ và một ví dụ truy vết MRV/forward checking. Kết quả thực tế sẽ được đo sau khi cài đặt, không đặt trước mức cải thiện.

## 7. Mã nguồn tham khảo và phần tự phát triển

- [AIMA Python — `csp.py`](https://github.com/aimacode/aima-python/blob/master/aima/csp.py): mã tham khảo cho CSP, quay lui, MRV và forward checking; có thể clone để đọc, chạy thử và đối chiếu thuật toán. Repository dùng [giấy phép MIT](https://github.com/aimacode/aima-python/blob/master/LICENSE); nếu sao chép hoặc sửa mã, giữ thông báo bản quyền và ghi rõ phần kế thừa.
- [Google OR-Tools — tài liệu CP-SAT](https://developers.google.com/optimization/cp/cp_solver): nguồn tham khảo cho cách mô hình hóa bài toán ràng buộc. Có thể dùng làm bộ giải đối chứng ở phần mở rộng, nhưng không thay thế phần thuật toán chính tự cài đặt.

**Đóng góp dự kiến của nhóm:** mô hình dữ liệu thời khóa biểu; hàm kiểm tra xung đột cho buổi học nhiều tiết; chuẩn bị miền giá trị; bộ giải CSP có MRV và forward checking; hàm chấm chất lượng lịch; giao diện và dữ liệu thử nghiệm; báo cáo thực nghiệm. Nếu lấy mã từ repository, báo cáo và README sẽ ghi đường dẫn, commit sử dụng, giấy phép và các thay đổi cụ thể.

## 8. Kế hoạch thực hiện và đầu ra

| Giai đoạn | Công việc | Kết quả kiểm tra được |
| --- | --- | --- |
| 1. Phân tích | Chuẩn hóa dữ liệu, định nghĩa biến/miền/ràng buộc, tạo dữ liệu mẫu | Tài liệu mô hình, CSV mẫu, bộ kiểm tra dữ liệu |
| 2. Thuật toán | Cài quay lui cơ bản, MRV, forward checking, kiểm tra lịch độc lập | Hai chế độ giải chạy được trên dữ liệu mẫu |
| 3. Sản phẩm | Tạo giao diện nhập dữ liệu, chạy thuật toán, xem/xuất lịch | Demo web hoàn chỉnh |
| 4. Đánh giá | Đo nhiều mức khó, phân tích vô nghiệm, viết báo cáo và chuẩn bị demo | Bảng/biểu đồ, báo cáo, README hướng dẫn chạy |

**Đầu ra bàn giao:** repository mã nguồn, dữ liệu thử nghiệm, hướng dẫn cài đặt và chạy, ứng dụng demo, báo cáo mô hình thuật toán và thực nghiệm, slide trình bày ngắn. Trước khi chốt đề tài, nhóm nên xác nhận với giảng viên rằng phạm vi xếp thời khóa biểu và dữ liệu mô phỏng phù hợp yêu cầu bài tập lớn của lớp.
