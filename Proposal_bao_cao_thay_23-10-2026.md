# PROPOSAL ĐỀ TÀI BÀI TẬP LỚN

**Học phần:** Nhập môn trí tuệ nhân tạo (IT3060)

**Tên đề tài:** Hệ thống hỗ trợ xếp thời khóa biểu học phần bằng trí tuệ nhân tạo

**Nhóm thực hiện:** *Bổ sung tên và mã sinh viên*

**Ngày báo cáo dự kiến:** 23/10/2026

## 1. Lý do chọn đề tài

Xếp thời khóa biểu là một công việc quen thuộc trong môi trường học tập, nhưng không đơn giản khi số lượng lớp học phần, giảng viên và phòng học tăng lên. Mỗi buổi học phải được đặt vào một khung giờ phù hợp, đồng thời tránh trùng phòng, trùng giảng viên và trùng lịch của nhóm sinh viên. Chỉ cần một giảng viên đổi giờ rảnh hoặc một phòng không còn sử dụng được, người xếp lịch có thể phải kiểm tra và điều chỉnh nhiều buổi liên quan.

Nhóm chọn đề tài này vì bài toán có tình huống sử dụng rõ ràng và gắn trực tiếp với kiến thức của môn Nhập môn trí tuệ nhân tạo. Thay vì chỉ tạo ra một thời khóa biểu, nhóm muốn tìm hiểu cách biểu diễn các điều kiện xếp lịch thành bài toán thỏa mãn ràng buộc, cách thuật toán tìm kiếm một lịch hợp lệ và vì sao một lựa chọn có thể gây xung đột cho các buổi học khác.

## 2. Mục tiêu và phạm vi

Mục tiêu của nhóm là xây dựng một ứng dụng có thể nhận danh sách buổi học, phòng học và giờ rảnh của giảng viên, sau đó tự động đề xuất một thời khóa biểu không vi phạm các điều kiện bắt buộc. Người dùng có thể xem lịch theo nhóm sinh viên, giảng viên hoặc phòng học; thay đổi một số điều kiện rồi chạy lại để quan sát kết quả. Ứng dụng cũng cho biết lý do một khung giờ đề xuất không phù hợp, chẳng hạn trùng phòng hoặc giảng viên không rảnh.

Về mặt học thuật, nhóm tập trung vào việc tự cài đặt và so sánh hai cách giải: quay lui cơ bản và quay lui có sử dụng các chiến lược MRV, degree heuristic, forward checking. Sau khi có lịch hợp lệ, nhóm thử cải thiện lịch theo các ưu tiên như hạn chế tiết muộn, giảm thời gian trống của nhóm sinh viên và tôn trọng giờ dạy mong muốn.

Để đề tài vừa sức với bài tập lớn, phiên bản hiện tại chỉ xếp lịch cho **một tuần học điển hình**. Mỗi buổi học thuộc một giảng viên và một nhóm sinh viên, kéo dài một hoặc hai tiết liên tiếp. Dữ liệu dùng để phát triển và trình diễn là dữ liệu mô phỏng, chưa phải dữ liệu thời khóa biểu chính thức. Những vấn đề như tuần chẵn/lẻ, lớp ghép phức tạp hay đăng ký học phần theo từng sinh viên nằm ngoài phạm vi hiện tại.

## 3. Phương án đề xuất

Nhóm triển khai phương án theo các bước sau:

**Bước 1 — Chuẩn bị và kiểm tra dữ liệu.** Đầu vào gồm danh sách buổi học, phòng học, giờ rảnh của giảng viên và cấu hình tuần học. Mỗi buổi có mã học phần, giảng viên, nhóm sinh viên, sĩ số, số tiết liên tiếp và loại phòng cần dùng. Mỗi phòng có sức chứa và loại phòng. Dữ liệu được lưu trong các tệp CSV/JSON để dễ chuẩn bị và chỉnh sửa. Trước khi xếp lịch, hệ thống kiểm tra các lỗi như thiếu thông tin, mã buổi bị trùng, phòng không đủ sức chứa hoặc khung giờ nằm ngoài tuần học. Nếu dữ liệu sai, ứng dụng báo lỗi để người dùng sửa thay vì tiếp tục tìm lịch.

**Bước 2 — Mô hình hóa thành bài toán CSP.** Mỗi buổi học là một biến cần gán vị trí. Một vị trí gồm **ngày, tiết bắt đầu và phòng học**. Ví dụ, buổi học dài hai tiết có thể được xếp vào thứ Hai từ tiết 1 đến tiết 2 tại phòng P101 nếu phòng đủ chỗ và giảng viên rảnh ở cả hai tiết. Những vị trí không đáp ứng điều kiện riêng của buổi học được loại ngay từ đầu. Khi ghép các buổi thành thời khóa biểu, hệ thống không cho phép các buổi chồng thời gian nếu dùng chung phòng, cùng giảng viên hoặc cùng nhóm sinh viên.

**Bước 3 — Tìm thời khóa biểu hợp lệ.** Nhóm dùng quay lui cơ bản làm cách giải đối chứng: chọn lần lượt từng buổi, thử các vị trí có thể xếp và quay lại khi lựa chọn hiện tại dẫn đến bế tắc. Ở cách giải cải tiến, **MRV** ưu tiên buổi còn ít vị trí để tránh để lại buổi khó đến cuối; nếu nhiều buổi có cùng số lựa chọn, hệ thống ưu tiên buổi liên quan đến nhiều buổi chưa xếp hơn. Sau mỗi lần đặt một buổi, **forward checking** loại khỏi các buổi còn lại những vị trí đã bị xung đột. Nếu một buổi không còn vị trí nào, thuật toán quay lui sớm. Nhóm giữ cả hai cách giải để có thể chạy trên cùng dữ liệu và quan sát sự khác biệt.

**Bước 4 — Kiểm tra và cải thiện kết quả.** Khi thuật toán tìm được lịch, một bộ kiểm tra độc lập rà soát lại toàn bộ buổi học và các điều kiện bắt buộc trước khi ứng dụng hiển thị hoặc xuất CSV. Sau đó, hệ thống tính điểm phạt cho tiết muộn, khoảng trống giữa các buổi của cùng nhóm và giờ dạy không đúng ưu tiên. Chức năng cải thiện lịch thử chuyển hoặc hoán đổi buổi học; chỉ giữ thay đổi vừa giảm điểm phạt vừa không tạo xung đột. Nếu tìm kiếm đã xét hết các khả năng mà không có lịch, hệ thống báo **vô nghiệm**. Nếu dừng vì hết thời gian, hệ thống báo **chưa tìm được lịch trong thời hạn**, không coi đó là kết luận vô nghiệm.

**Bước 5 — Trình bày trên ứng dụng và đánh giá.** Giao diện Streamlit cho phép chọn dữ liệu mẫu hoặc tải tệp mới, chọn một trong hai bộ giải, điều chỉnh trọng số ưu tiên, xem thời khóa biểu theo nhóm sinh viên, giảng viên hoặc phòng học và tải lịch về. Người dùng cũng có thể thay đổi một ô giờ rảnh rồi chạy lại, hoặc chọn một vị trí đề xuất để xem lý do bị từ chối. Khi báo cáo, nhóm sẽ trình diễn luồng này và so sánh hai bộ giải dựa trên tính hợp lệ của lịch, số bước tìm kiếm, số lần quay lui, thời gian chạy và chất lượng lịch. Các nhận xét sẽ gắn với bộ dữ liệu đã thử, vì dữ liệu hiện tại vẫn là dữ liệu mô phỏng.

## 4. Tiến độ hiện tại

Đến thời điểm báo cáo, nhóm đã có bản ứng dụng chạy được. Phần xử lý dữ liệu, kiểm tra ràng buộc, hai bộ giải CSP, chấm điểm và cải thiện lịch đã được cài đặt. Giao diện cho phép sử dụng dữ liệu mẫu hoặc tải dữ liệu mới, điều chỉnh giờ rảnh trong phiên làm việc, xem lịch và tải kết quả. Nhóm cũng đã chuẩn bị dữ liệu mô phỏng, bộ kiểm thử, báo cáo kỹ thuật và slide để phục vụ trình bày.

Các chức năng chính đã được chạy thử và bộ demo tạo được lịch hợp lệ. Kết quả thực nghiệm bước đầu cho thấy chiến lược MRV và forward checking giúp giảm số lựa chọn phải xét trong những tình huống đã thử. Tuy nhiên, thời gian chạy còn phụ thuộc vào đặc điểm dữ liệu và chi phí xử lý của thuật toán, nên nhóm chưa xem đây là kết luận chung cho mọi bài toán xếp lịch. Phần giải thích hiện tập trung vào xung đột của một khung giờ cụ thể; chưa xác định đầy đủ tập nguyên nhân tối thiểu khi cả bài toán vô nghiệm.

## 5. Kế hoạch dự định tiếp theo

Trước hết, nhóm sẽ tiếp tục bổ sung các bộ dữ liệu có tình huống gần thực tế hơn, chẳng hạn nhiều lớp cùng dùng một số phòng và giảng viên dạy nhiều nhóm. Từ đó, nhóm kiểm tra xem hai thuật toán hoạt động ra sao khi ràng buộc chặt hơn, đồng thời rà soát những quy tắc xếp lịch có thể còn thiếu.

Tiếp theo, nhóm sẽ hoàn thiện phần trình bày: chọn một ví dụ ngắn để giải thích từng bước chọn biến và loại giá trị, làm rõ sự khác nhau giữa lịch hợp lệ và lịch thuận tiện, và thống nhất nội dung giữa ứng dụng, báo cáo và slide. Nhóm cũng muốn nhận góp ý của thầy về phạm vi một tuần học điển hình, việc sử dụng dữ liệu mô phỏng và những tiêu chí quan trọng nhất cần đánh giá trước khi hoàn thiện bài tập lớn.
