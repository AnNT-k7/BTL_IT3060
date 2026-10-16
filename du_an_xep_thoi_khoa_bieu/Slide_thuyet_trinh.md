# Xếp thời khóa biểu học phần bằng CSP

Bài tập lớn — Nhập môn trí tuệ nhân tạo

Demo trên dữ liệu mô phỏng; lịch lặp lại theo một tuần học điển hình.

---

# Vấn đề cần giải quyết

- Mỗi buổi học cần một ngày, tiết bắt đầu và phòng phù hợp.
- Không được trùng phòng, giảng viên hoặc nhóm sinh viên.
- Lịch hợp lệ vẫn có thể bất tiện vì tiết muộn và khoảng trống.
- Khi đổi giờ rảnh, cần xếp lại và giải thích xung đột.

---

# Biểu diễn thành CSP

- Biến: một buổi học Sᵢ.
- Miền: các bộ (ngày, tiết bắt đầu, phòng) phù hợp với chính buổi đó.
- Ràng buộc cứng: sức chứa, loại phòng, giờ rảnh, không chồng thời gian.
- Ràng buộc mềm: tiết muộn, tiết trống, giờ không ưa thích.

---

# Hai chiến lược tìm kiếm

- A — Quay lui cơ bản: chọn buổi theo thứ tự dữ liệu.
- B — MRV: chọn buổi còn ít vị trí; degree phá hòa.
- Forward checking loại sớm vị trí xung đột ở các buổi liên quan.
- Khi quay lui, khôi phục chính xác các giá trị đã bị loại.

---

# Sản phẩm demo

- Nạp CSV mẫu hoặc tải bộ dữ liệu mới.
- Chọn bộ giải, thời gian chạy và trọng số điểm phạt.
- Xem lịch dạng lưới theo nhóm, giảng viên hoặc phòng; xuất CSV.
- Thử một khung giờ đề xuất để xem lý do bị từ chối.

---

# Kết quả thực nghiệm

- 170 phép đo: 5 bộ khả thi × 3 seed × 5 lần lặp × 2 thuật toán, cùng 2 ca riêng.
- 40 buổi thông thường: cơ bản xét 1.361 nút / 11,86 ms; MRV + FC xét 40 nút / 25,40 ms.
- 40 buổi ràng buộc chặt: cơ bản quay lui 32,3 lần; MRV + FC không quay lui.
- Ca vô nghiệm: cơ bản xét 53.823 nút; MRV + FC xét 3 nút.
- Tất cả lịch được công bố có 0 vi phạm cứng.

---

# Giải thích kết quả

- MRV + FC cắt giảm nút, nhưng việc cập nhật miền có chi phí.
- Bộ thông thường còn dễ; bộ ràng buộc chặt tạo ra quay lui nhưng có cấu trúc nhân tạo.
- Ở bộ tight20/tight40, MRV + FC không quay lui; nó vẫn chạy lâu hơn do cập nhật miền.
- Không kết luận một thuật toán luôn nhanh hơn trên mọi dữ liệu.

---

# Kịch bản trình diễn và hướng tiếp theo

- Chạy dữ liệu demo → xem lịch hợp lệ và điểm phạt.
- Khóa một tiết của giảng viên → chạy lại → so sánh số buổi đổi vị trí.
- Chọn một vị trí xung đột → đọc lý do; chạy bộ vô nghiệm để xem UNSAT.
- Tiếp tục thử dữ liệu khó hơn và đối chiếu yêu cầu thực tế với giảng viên.
