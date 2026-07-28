# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5A: Trace Analyst*

**Đề tài nhóm:** 🏢 Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

> **Mục tiêu:** Chứng minh bài toán "Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn" CẦN dùng ReAct Agent chứ không chỉ Chatbot thông thường.

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Quy trình tuyển dụng đòi hỏi chuỗi suy luận nhiều bước: (1) Tiếp nhận yêu cầu tuyển dụng từ HR → (2) Truy xuất danh sách hồ sơ ứng viên → (3) So khớp kỹ năng/kinh nghiệm với JD → (4) Chấm điểm & xếp hạng ứng viên → (5) Kiểm tra lịch trống của interviewer → (6) Đề xuất lịch phỏng vấn. Mỗi bước phụ thuộc kết quả bước trước, Chatbot thuần không thể tự xâu chuỗi được. |
| 🛠️ **Tool Interaction** | `5/5` | Cần nhiều công cụ chuyên biệt: tra cứu DB hồ sơ ứng viên, so khớp CV với JD, kiểm tra lịch trống interviewer, đặt lịch phỏng vấn, gửi thông báo cho ứng viên. Chatbot thuần chỉ tư vấn chung chung mà không truy cập được dữ liệu thực tế của công ty. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả mỗi bước quyết định hành động tiếp theo: tìm 0 ứng viên → mở rộng tiêu chí; điểm match thấp → loại và chuyển ứng viên khác; interviewer bận → tìm slot khác hoặc interviewer thay thế. Đây là hành vi dynamic branching điển hình mà Chatbot không làm được. |
| ⏳ **Long Horizon** | `4/5` | Quy trình trải qua 4-6 bước xử lý tuần tự (tiếp nhận JD → lọc CV → chấm điểm → xếp hạng → kiểm lịch → đặt hẹn). Trừ 1 điểm vì mỗi phiên thường xử lý 1 vị trí tuyển dụng, không yêu cầu memory xuyên phiên như Cấp 4 Autonomous Agent. |
| **TỔNG ĐIỂM FIT** | **19/20** | **KẾT LUẬN: BÀI TOÁN RẤT PHÙ HỢP VỚI REACT AGENT! ✅** |

---

## 🔍 2. SO SÁNH PHẢN HỒI CHATBOT VS AGENT (Sẽ điền ở Mốc 2-3)

> *Phần này sẽ được Role 5A cập nhật sau khi chạy thử Chatbot Baseline và ReAct Agent.*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *(Chờ kết quả chạy thử ở Mốc 2)*
* **Nhận xét**: *(Chờ đánh giá)*

### 🧠 ReAct Agent:
* **Trace Log**: *(Chờ kết quả chạy thử ở Mốc 3)*
* **Nhận xét**: *(Chờ đánh giá)*
