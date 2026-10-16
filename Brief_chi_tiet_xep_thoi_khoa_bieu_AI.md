---
title: Brief chi tiết — Hệ thống xếp thời khóa biểu học phần thông minh
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Brief chi tiết: Hệ thống xếp thời khóa biểu học phần thông minh

## 1. Ý tưởng trong một đoạn

Xây dựng ứng dụng web giúp xếp lịch cho **một tuần học điển hình** của một tập lớp học phần quy mô khoa/khóa. Người dùng cung cấp buổi học cần xếp, giảng viên, nhóm sinh viên, phòng học, khung giờ và các điều kiện sử dụng. Ứng dụng tìm một thời khóa biểu không trùng phòng, giảng viên hoặc nhóm sinh viên; sau đó cải thiện lịch theo các ưu tiên như tránh tiết muộn, giảm khoảng trống và tôn trọng giờ dạy mong muốn. Điểm nghiên cứu nằm ở việc **mô hình hóa bài toán thành CSP, tự xây dựng và so sánh các chiến lược tìm kiếm**, đồng thời trình bày kết quả qua một giao diện có thể thao tác.

Đề tài bám sát bài giảng của môn *Nhập môn trí tuệ nhân tạo*: [L6 — Thỏa mãn ràng buộc](LMS/L6_Thoa_man_rang_buoc.pdf) trình bày quay lui, MRV, forward checking và AC-3; [L4 — Tìm kiếm với tri thức bổ sung](LMS/L4-Tim%20kiem%20voi%20tri%20thu%20bo%20sung.pdf) trình bày cách dùng tri thức miền để điều hướng tìm kiếm.

## 2. Bối cảnh, người dùng và vấn đề

**Người dùng chính:** sinh viên/nhóm sinh viên đóng vai người lập lịch cho một khoa nhỏ. Trong demo, người dùng có thể là giảng viên hoặc trợ giảng muốn kiểm tra nhanh một lịch dự kiến.

**Vấn đề cụ thể:** một buổi học có nhiều khả năng xếp; mỗi quyết định có thể ảnh hưởng đến những buổi khác cùng dùng phòng, cùng giảng viên hoặc cùng nhóm sinh viên. Xếp thủ công vẫn khả thi khi ít buổi, nhưng khó kiểm tra đầy đủ và khó điều chỉnh khi thêm một điều kiện mới. Một lịch “không trùng” cũng chưa chắc thuận tiện: có thể dồn quá nhiều buổi vào cuối ngày hoặc để các nhóm sinh viên chờ lâu giữa hai buổi.

**Giá trị của sản phẩm:** rút ngắn thao tác tìm lịch, đảm bảo các quy tắc bắt buộc bằng kiểm tra tự động, cho phép thay đổi ưu tiên rồi quan sát tác động, và cung cấp số liệu thực nghiệm để thấy chiến lược AI nào hiệu quả hơn.

## 3. Mục tiêu và ranh giới

### Mục tiêu bắt buộc

1. Nhập dữ liệu hợp lệ từ CSV/JSON mẫu và báo lỗi rõ ràng với dữ liệu sai.
2. Tìm một lịch thỏa tất cả ràng buộc cứng, hoặc kết luận chưa tìm được lịch trong giới hạn tính toán đã đặt.
3. Cài đặt hai chế độ giải: **quay lui cơ bản** và **quay lui + MRV + forward checking**.
4. Có bộ kiểm tra lịch độc lập với bộ giải; mọi lịch xuất ra phải qua bộ kiểm tra này.
5. Hiển thị lịch, thống kê tìm kiếm và điểm chất lượng; cho phép tải kết quả về.
6. Tổ chức thực nghiệm trên nhiều mức khó, cùng dữ liệu và cùng giới hạn thời gian.

### Phạm vi phiên bản đầu

- Lịch lặp lại theo tuần, từ thứ Hai đến thứ Sáu; 6–8 tiết mỗi ngày.
- Mỗi buổi chiếm 1 hoặc 2 tiết liền nhau trong cùng một phòng.
- Mỗi buổi thuộc đúng một giảng viên và một nhóm sinh viên; một nhóm đại diện cho tập sinh viên học cùng lịch.
- Phòng có sức chứa và có thể có loại phòng (thường/máy tính). Điều kiện loại phòng là tùy chọn nếu dữ liệu có cung cấp.
- Chưa xử lý lịch tuần chẵn/lẻ, buổi học trực tuyến, đăng ký học phần của từng sinh viên, hoặc phân bổ giảng viên tự động.

**Giả định cần xác nhận khi bắt đầu triển khai:** số buổi được coi là dữ liệu đầu vào đã chốt; mục tiêu là xếp lịch cho các buổi, không quyết định mở bao nhiêu lớp học phần.

## 4. Trải nghiệm sử dụng

1. Người dùng mở ứng dụng và chọn bộ dữ liệu mẫu hoặc tải các file CSV.
2. Hệ thống xác thực: mã không trùng, khóa ngoại tồn tại, số lượng sinh viên không âm, thời lượng 1–2 tiết, khung giờ nằm trong tuần định nghĩa.
3. Người dùng chọn chế độ giải, giới hạn thời gian chạy và trọng số các ưu tiên mềm.
4. Ứng dụng chạy bộ giải, hiển thị trạng thái `Có lịch hợp lệ`, `Không tìm thấy lịch trong thời hạn`, hoặc `Đã chứng minh vô nghiệm` nếu thuật toán duyệt hết không gian tìm kiếm.
5. Khi có lịch, người dùng xem lưới tuần theo nhóm sinh viên/giảng viên/phòng, bảng chi tiết, điểm phạt và số liệu thuật toán; sau đó xuất CSV.
6. Người dùng khóa một khung giờ hoặc sửa dữ liệu, chạy lại và so sánh hai kết quả.

Điểm khác biệt trong demo là người xem có thể **thay đổi một ràng buộc và thấy thuật toán phản ứng**. Một màn hình “giải thích quyết định” hiển thị ví dụ nhỏ: biến được chọn theo MRV, số giá trị còn lại trước/sau forward checking, và lý do các giá trị bị loại. Với bài toán lớn, màn hình chỉ ghi một số bước tiêu biểu để tránh quá tải.

## 5. Dữ liệu đầu vào đề xuất

Các file là giao diện dữ liệu dự kiến; tên trường có thể chỉnh khi cài đặt, nhưng ý nghĩa phải nhất quán trong mã, README và báo cáo.

| Tập dữ liệu | Trường chính | Ví dụ/ý nghĩa |
| --- | --- | --- |
| `sessions.csv` | `session_id, course_id, teacher_id, group_id, size, duration, room_type` | Một buổi học của một lớp; `duration` là số tiết liền nhau |
| `rooms.csv` | `room_id, capacity, room_type` | Phòng P101, sức chứa 60, loại thường |
| `availability.csv` | `teacher_id, day, period, available` | Giảng viên có thể dạy ở từng tiết hay không |
| `preferences.csv` | `teacher_id, day, period, preference` | Điểm ưu tiên của khung giờ; có thể bỏ trống |
| `config.json` | `days, periods_per_day, weights, time_limit_seconds` | Cấu hình tuần và trọng số điểm phạt |

Ví dụ một dòng `sessions.csv`:

```csv
session_id,course_id,teacher_id,group_id,size,duration,room_type
S01,IT3160,GV01,IT2-02,58,2,normal
```

**Dữ liệu thực nghiệm:** tạo dữ liệu mô phỏng có seed và script sinh dữ liệu. Dự kiến 3 cấp độ: nhỏ (10–15 buổi), vừa (20–30 buổi), lớn (35–40 buổi). Mỗi cấp độ có nhiều biến thể để tránh rút kết luận từ một lịch đơn lẻ. Bộ vô nghiệm có chủ đích nên kèm lý do đã biết, chẳng hạn giảng viên chỉ rảnh 2 tiết nhưng cần dạy 2 buổi, mỗi buổi 2 tiết. Dữ liệu mô phỏng không được giới thiệu là lịch chính thức của trường.

## 6. Mô hình CSP và hàm chất lượng

### Biến và miền

Với mỗi buổi học `S_i`, tạo biến `X_i`. Một giá trị của `X_i` là bộ `(day, start_period, room_id)`. Buổi có thời lượng `d_i` chiếm các tiết từ `start_period` đến `start_period + d_i - 1`. Miền ban đầu chỉ giữ các giá trị thỏa điều kiện một biến: nằm trong giờ học, phòng đủ lớn/đúng loại, giảng viên rảnh trong toàn bộ buổi.

**Ví dụ nhỏ:** buổi `S01` học 2 tiết, có 58 sinh viên, giảng viên `GV01`. Nếu phòng P101 chứa 60 người và GV01 rảnh thứ Hai tiết 1–2, `(Thứ Hai, tiết 1, P101)` thuộc miền. Nếu P102 chỉ chứa 45 người, cùng khung giờ với P102 bị loại ngay.

### Ràng buộc cứng

Hai buổi có thời gian giao nhau không được có cùng phòng, cùng giảng viên hoặc cùng nhóm sinh viên. Một buổi phải được gán đúng một giá trị trong miền. Nếu có danh sách khung giờ cấm hoặc buổi cố định, miền của biến được thu hẹp tương ứng. Bộ kiểm tra độc lập duyệt tất cả buổi trong kết quả và đếm số vi phạm theo từng loại.

### Ràng buộc mềm và cách chấm

Chỉ chấm khi lịch đã thỏa ràng buộc cứng. Công thức dự kiến:

`cost = w1 × late_periods + w2 × student_gaps + w3 × preference_penalty`

- `late_periods`: tổng số tiết học ở các tiết được định nghĩa là muộn, ví dụ 2 tiết cuối ngày.
- `student_gaps`: tổng số tiết trống **nằm giữa** hai buổi trong cùng ngày của từng nhóm, không tính tiết trước buổi đầu hay sau buổi cuối.
- `preference_penalty`: tổng mức phạt khi buổi học không rơi vào thời gian giảng viên ưa thích; chỉ áp dụng nếu có dữ liệu ưu tiên.

Trọng số mặc định phải được công bố trong báo cáo; giao diện cho phép thay đổi để xem trade-off. Không dùng tổng điểm phạt để che một vi phạm cứng: lịch có xung đột luôn bị loại, bất kể điểm phạt thấp.

## 7. Thiết kế thuật toán

### Bộ giải A — quay lui cơ bản

Chọn buổi đầu tiên chưa được gán theo thứ tự file, thử lần lượt từng giá trị trong miền, kiểm tra xung đột với các buổi đã gán; nếu không còn giá trị, quay lui. Đây là mốc so sánh để đo tác dụng của chiến lược chọn biến và suy diễn.

### Bộ giải B — quay lui có heuristic

- **MRV:** ưu tiên buổi có ít giá trị hợp lệ còn lại nhất.
- **Phá hòa bằng degree:** nếu hai buổi có số giá trị bằng nhau, ưu tiên buổi có nhiều ràng buộc với các buổi chưa gán.
- **Forward checking:** sau mỗi phép gán, loại giá trị xung đột khỏi miền của các buổi liên quan; quay lui ngay nếu một miền rỗng.
- **Khôi phục miền:** khi quay lui, trả lại chính xác các giá trị đã loại ở bước tương ứng.

Mã giả rút gọn:

```text
solve(assignment, domains):
    if all sessions assigned: return assignment
    x = choose_unassigned_with_MRV_and_degree(domains)
    for value in ordered_domain(x):
        if value does not conflict with assignment:
            assign x = value
            removed = forward_check_neighbors(x, value, domains)
            if no domain is empty:
                result = solve(assignment, domains)
                if result exists: return result
            restore(removed)
            unassign x
    return no_solution
```

### Cải thiện chất lượng lịch

Sau khi tìm được một lịch hợp lệ, chạy tìm kiếm cục bộ có giới hạn thời gian: thử chuyển một buổi sang giá trị khác trong miền hoặc hoán đổi vị trí hai buổi; chỉ giữ thay đổi vượt qua bộ kiểm tra cứng và làm giảm `cost`. Để báo cáo rõ tác dụng của từng bước, kết quả sau tối ưu được ghi riêng với kết quả CSP ban đầu. Nếu phần này chưa kịp hoàn thiện, trọng tâm bắt buộc vẫn là hai bộ giải CSP và thực nghiệm so sánh.

**Giải thích vô nghiệm:** forward checking có thể chỉ ra miền của buổi nào vừa rỗng và do phép gán nào, nhưng đây là **dấu vết cục bộ**, chưa nhất thiết là tập nguyên nhân tối thiểu của toàn bài toán. Chỉ ghi “đã chứng minh vô nghiệm” khi bộ giải đã duyệt hết các nhánh; nếu hết thời gian, ghi “chưa tìm thấy lịch trong thời hạn”.

## 8. Yêu cầu chức năng và tiêu chí hoàn thành

| Mã | Yêu cầu | Cách kiểm tra |
| --- | --- | --- |
| F1 | Tải dữ liệu và báo lỗi theo dòng/trường | CSV có mã giảng viên không tồn tại phải bị từ chối kèm vị trí lỗi |
| F2 | Tạo lịch bằng hai chế độ giải | Cùng một bộ dữ liệu chạy được trên cả hai chế độ |
| F3 | Kiểm tra lịch độc lập | Một lịch cố ý trùng phòng/giảng viên/nhóm phải bị phát hiện |
| F4 | Hiển thị lịch theo 3 góc nhìn | Bộ lọc phòng, giảng viên, nhóm cho kết quả nhất quán |
| F5 | Trình bày số liệu thuật toán | Có thời gian, số nút duyệt, số lần quay lui, trạng thái kết thúc |
| F6 | Tính và giải thích điểm phạt | Tổng điểm bằng tổng có trọng số của các thành phần |
| F7 | Xuất dữ liệu kết quả | CSV xuất ra nạp lại được và qua bộ kiểm tra lịch |
| F8 | Xử lý dữ liệu vô nghiệm/hết giờ | Hai trạng thái được phân biệt rõ trong giao diện |

## 9. Kế hoạch đánh giá

Thực nghiệm so sánh A và B trên bộ dữ liệu nhỏ, vừa, lớn; mỗi cấu hình có nhiều biến thể được tạo bằng seed đã lưu. Cùng một máy, cùng bộ dữ liệu, cùng giới hạn thời gian và cùng cách đo. Không so sánh thời gian của hai thuật toán trên các tập đầu vào khác nhau.

**Chỉ số chính:** tỷ lệ tìm được lịch hợp lệ trong thời hạn, thời gian chạy, số nút đã xét, số lần quay lui. **Chỉ số chất lượng:** số vi phạm cứng (bắt buộc bằng 0), điểm phạt trước/sau tìm kiếm cục bộ. **Chỉ số giải thích:** với bộ vô nghiệm có chủ đích, giao diện nêu được một dấu vết hợp lý và không nhầm “hết giờ” với “vô nghiệm”.

Báo cáo nên có bảng kết quả theo từng bộ dữ liệu, biểu đồ thời gian/số nút theo quy mô, một ví dụ truy vết thuật toán, và phần phân tích trường hợp heuristic không cải thiện hoặc làm tăng chi phí tính toán. Nếu có so sánh thêm với OR-Tools, đặt ở mục mở rộng và nêu rõ đó là bộ giải thư viện.

## 10. Công nghệ, tài liệu tham khảo và tính độc lập

- **Ngôn ngữ:** Python. **Giao diện:** Streamlit. **Dữ liệu:** CSV/JSON. **Biểu đồ:** thư viện vẽ nhẹ theo nhu cầu.
- [AIMA Python, module CSP](https://github.com/aimacode/aima-python/blob/master/aima/csp.py) dùng để nghiên cứu cấu trúc thuật toán và đối chiếu kết quả. Repository có [giấy phép MIT](https://github.com/aimacode/aima-python/blob/master/LICENSE). Nếu lấy mã, giữ thông báo giấy phép, ghi commit nguồn và phần đã chỉnh sửa.
- [Google OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver) là nguồn tham khảo cho mô hình ràng buộc hoặc bộ giải đối chứng tùy thời gian. Không dùng kết quả từ thư viện để thay thế phần quay lui/MRV/forward checking tự xây dựng.

Các phần nhóm cần thể hiện rõ trong mã và báo cáo: mô hình hóa buổi học nhiều tiết, kiểm tra xung đột, xây dựng miền, cài bộ giải A/B, bộ kiểm tra độc lập, hàm điểm phạt, tạo dữ liệu thực nghiệm và phân tích kết quả. README ghi cách chạy, cấu trúc dữ liệu, phiên bản thư viện và nguồn mã kế thừa.

## 11. Kế hoạch thực hiện gợi ý

| Tuần | Trọng tâm | Bằng chứng hoàn thành |
| --- | --- | --- |
| 1 | Chốt mô hình, định dạng CSV, tạo dữ liệu nhỏ và bộ kiểm tra | Có mẫu đầu vào/đầu ra và các ca xung đột rõ ràng |
| 2 | Cài quay lui cơ bản, MRV, forward checking | Hai bộ giải cùng trả lịch hợp lệ ở ca nhỏ |
| 3 | Xây giao diện, xuất CSV, bộ dữ liệu vừa/lớn | Demo nhập → giải → xem → xuất chạy liên tục |
| 4 | Tối ưu lịch, thực nghiệm, báo cáo và slide | Bảng số liệu tái lập được, minh họa thuật toán, demo ổn định |

Nếu nhóm có nhiều thành viên, có thể chia theo mô hình dữ liệu và kiểm tra; thuật toán; giao diện; thực nghiệm/báo cáo. Việc ghép mã nên diễn ra từ tuần 2 để tránh mỗi phần dùng một định dạng dữ liệu khác nhau.

## 12. Rủi ro và quyết định còn mở

| Rủi ro/điểm mở | Cách xử lý dự kiến |
| --- | --- |
| Dữ liệu mô phỏng quá dễ, hai thuật toán chạy gần như giống nhau | Tạo nhiều mức mật độ ràng buộc; công bố cách sinh dữ liệu và seed |
| Dữ liệu quá chặt, không có lịch | Giữ bộ hợp lệ đã biết lời giải; có bộ vô nghiệm riêng để thử xử lý lỗi |
| Quay lui cơ bản quá chậm | Đặt giới hạn thời gian và báo trạng thái hết giờ; dùng quy mô nhỏ để minh họa đầy đủ |
| Giao diện ngốn thời gian, lấn phần thuật toán | Hoàn thiện CLI/bộ giải và kiểm tra độc lập trước; UI chỉ cần ba màn hình chính |
| “Giải thích vô nghiệm” bị diễn đạt quá chắc chắn | Phân biệt dấu vết miền rỗng, bằng chứng duyệt hết và hết thời gian |

**Cần xác nhận với giảng viên:** có cho phép dùng dữ liệu mô phỏng và thư viện giao diện; yêu cầu cụ thể về báo cáo, số trang, trích dẫn, hình thức nộp và quy mô nhóm. Các mục này chưa được suy ra từ tài liệu bài giảng hiện có.

## 13. Đầu ra cuối cùng

Một repository có mã nguồn và giấy phép/ghi công nguồn tham khảo; các bộ dữ liệu và script sinh dữ liệu; ứng dụng demo; README chạy lại được; báo cáo trình bày mô hình CSP, thuật toán, thực nghiệm và giới hạn; slide ngắn với kịch bản demo thay đổi ràng buộc trực tiếp.
