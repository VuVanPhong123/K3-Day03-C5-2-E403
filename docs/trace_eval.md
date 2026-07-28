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

## 🔍 2. PHẢN HỒI CHATBOT BASELINE (MỐC 2)

> **Mục tiêu Mốc 2:** Ghi lại phản hồi Chatbot gốc, quan sát xem có bị ảo giác (hallucination) hoặc bất lực trước yêu cầu cần dữ liệu thực tế không.

**LLM Provider:** GeminiProvider | **Model:** gemini-3.1-flash-lite

### Test Case #2 — 🟢 Đơn giản (Chỉ cần Tool đơn)

**Câu hỏi:** *"CV của Nguyễn Văn A có bao nhiêu năm kinh nghiệm?"*

**🤖 Chatbot Baseline trả lời:**

> Chào bạn, tôi là Trợ lý Sàng lọc Hồ sơ.
>
> Hiện tại, bạn **chưa cung cấp nội dung CV của ứng viên Nguyễn Văn A** trong hội thoại này. Do đó, tôi không thể xác định được số năm kinh nghiệm của ứng viên.
>
> Để tôi có thể hỗ trợ bạn sàng lọc và đánh giá, vui lòng cung cấp:
> 1. **Thông tin CV** (hoặc tóm tắt kinh nghiệm làm việc) của ứng viên Nguyễn Văn A.
> 2. **Mô tả công việc (JD)** mà bạn đang tuyển dụng.
>
> Sau khi nhận được thông tin này, tôi sẽ thực hiện phân tích theo đúng quy trình và định dạng bạn đã yêu cầu.

### 📝 Nhận xét của Role 5A (Mốc 2):

| Tiêu chí đánh giá | Kết quả | Ghi chú |
| :--- | :---: | :--- |
| **Factual Correctness** | ⚠️ Không trả lời được | Chatbot thừa nhận không có dữ liệu — đúng về mặt logic nhưng không giải quyết được nhu cầu HR |
| **Grounding (Bằng chứng)** | ❌ Không có | Không có bất kỳ evidence thực tế nào vì không truy cập được DB ứng viên |
| **Hallucination (Ảo giác)** | ✅ Không bịa | Chatbot KHÔNG bịa số năm kinh nghiệm — đây là hành vi an toàn (safe fallback) nhờ `CHATBOT_BASELINE_PROMPT` đã ràng buộc tốt |
| **Tool Calls** | 0 lần | Chatbot Baseline không có tool, đúng thiết kế |
| **Usefulness (Hữu ích)** | ❌ Thấp | Người dùng HR cần câu trả lời ngay lập tức từ DB, Chatbot bắt phải nhập lại CV → không thực tế |

**🏷️ Phân loại output:** `safe fallback` — An toàn nhưng vô dụng trong bối cảnh thực tế HR.

**⚡ Kết luận Mốc 2:** Chatbot Baseline tuân thủ prompt tốt (không ảo giác), nhưng **hoàn toàn bất lực** trước câu hỏi cần truy xuất dữ liệu thực tế. Đây chính là lý do bài toán tuyển dụng CẦN ReAct Agent với Tools.

---

## 🧠 3. TRACE LOG REACT AGENT (MỐC 3)

> **Mục tiêu Mốc 3:** Trích xuất chuỗi `Thought → Action → Observation` hoàn chỉnh để chứng minh Agent suy luận đúng và gọi Tool có bằng chứng.

**Câu hỏi:** *"Đánh giá CV_001 cho vị trí backend_senior và demo đặt lịch phỏng vấn."*

**Available Tools:** `get_candidate_profile`, `get_job_requirements`, `evaluate_fit`, `check_interview_schedule`, `schedule_interview`, `send_notification`, `get_interview_status`

---

### 🔄 Step 1/4 — Lấy hồ sơ ứng viên

```
Thought: Need the candidate profile before screening.
Action: get_candidate_profile[CV_001]
```

**Observation:**
```json
{
  "error": false,
  "candidate_id": "CV_001",
  "data": {
    "name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone": "0901234567",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
    "experience_years": 4,
    "education": "Đại học Bách Khoa TP.HCM - Kỹ sư CNTT",
    "applied_job_id": "backend_senior",
    "cv_summary": "4 năm kinh nghiệm phát triển backend với Python/FastAPI, từng xây dựng hệ thống microservices xử lý 1M+ request/ngày."
  }
}
```

---

### 🔄 Step 2/4 — Lấy yêu cầu công việc

```
Thought: Need the job requirements to compare against the CV.
Action: get_job_requirements[backend_senior]
```

**Observation:**
```json
{
  "error": false,
  "job_id": "backend_senior",
  "data": {
    "title": "Senior Backend Engineer",
    "department": "Engineering",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
    "experience_min": 3,
    "salary_range": "25,000,000 - 40,000,000 VNĐ",
    "location": "TP.HCM (Hybrid)"
  }
}
```

---

### 🔄 Step 3/4 — Đánh giá mức độ phù hợp

```
Thought: Candidate and job data are available, so evaluate fit.
Action: evaluate_fit[CV_001, backend_senior]
```

**Observation:**
```json
{
  "error": false,
  "candidate_id": "CV_001",
  "job_id": "backend_senior",
  "fit_percentage": 90,
  "matched_skills": ["docker", "fastapi", "python", "postgresql"],
  "missing_skills": ["redis"],
  "skill_score": 80.0,
  "experience_score": 100,
  "recommendation": "🟢 RẤT PHÙ HỢP - Ưu tiên phỏng vấn",
  "candidate_experience": 4,
  "job_required_experience": 3
}
```

---

### 🔄 Step 4/4 — Kiểm tra lịch → Đặt hẹn → Gửi thông báo

```
Thought: Fit is strong enough for a demo interview scheduling step.
Action: check_interview_schedule[2026-08-05]
```

**Observation:**
```json
{
  "date": "2026-08-05",
  "available_slots": ["09:00", "14:00", "15:00"],
  "booked_slots": ["10:00"],
  "total_slots": 4,
  "available_count": 3
}
```

```
Action: schedule_interview[CV_001, 2026-08-05, 09:00, backend_senior]
```

**Observation:**
```json
{
  "status": "success",
  "interview_id": "INT_002",
  "candidate_name": "Nguyễn Văn A",
  "candidate_email": "nguyenvana@email.com",
  "date": "2026-08-05",
  "time": "09:00",
  "message": "✅ Lịch phỏng vấn đã đặt thành công cho Nguyễn Văn A vào 2026-08-05 lúc 09:00."
}
```

```
Action: send_notification[CV_001, interview_scheduled]
```

**Observation:**
```json
{
  "status": "sent",
  "recipient": "nguyenvana@email.com",
  "notification_type": "interview_scheduled",
  "subject": "Lời mời phỏng vấn - Công ty XYZ",
  "message": "✅ Thông báo 'interview_scheduled' đã gửi tới nguyenvana@email.com."
}
```

---

### 🏁 Final Answer

```
Thought: I have candidate data, job data, fit evidence, schedule availability,
         booking confirmation, and notification status.
Final Answer: CV_001 is a strong match for backend_senior. The demo scheduled
              an interview on 2026-08-05 at 09:00 and generated a notification
              confirmation.
```

---

## 📊 4. SO SÁNH CHATBOT VS REACT AGENT (BẢNG TỔNG HỢP)

| Tiêu chí | 🤖 Chatbot Baseline | 🧠 ReAct Agent | Winner |
| :--- | :--- | :--- | :---: |
| **Factual Correctness** | ❌ Không trả lời được (yêu cầu user nhập lại CV) | ✅ Trả lời chính xác: 4 năm kinh nghiệm, skills match 80%, fit 90% | Agent |
| **Grounding** | ❌ Không có evidence | ✅ Mỗi bước đều có Observation từ tool thực tế | Agent |
| **Hallucination** | ✅ Không bịa (safe fallback) | ✅ Không bịa (dựa trên evidence) | Hòa |
| **Tool Selection** | N/A (0 tool calls) | ✅ Gọi đúng 6 tools theo thứ tự logic | Agent |
| **Termination** | Dừng ngay sau 1 LLM call | ✅ Dừng đúng lúc sau 4 steps + Final Answer | Agent |
| **Số bước xử lý** | 1 bước (chỉ LLM) | 4 steps × 6 tool calls | Agent phức tạp hơn |
| **Usefulness** | ❌ Thấp — bất lực trước yêu cầu thực tế | ✅ Cao — hoàn thành trọn vẹn quy trình sàng lọc + đặt hẹn + thông báo | Agent |

### 📝 Nhận xét tổng hợp:

1. **Chatbot Baseline** tuân thủ prompt tốt (không hallucinate), nhưng **hoàn toàn bất lực** trước bất kỳ câu hỏi nào yêu cầu truy xuất dữ liệu ứng viên, kiểm tra lịch, hoặc thực hiện hành động. Trong bối cảnh HR, điều này khiến chatbot **không có giá trị sử dụng thực tế**.

2. **ReAct Agent** chứng minh rõ ràng sức mạnh của chuỗi `Thought → Action → Observation`:
   - **Step 1-2**: Thu thập dữ liệu (CV + JD) — grounding evidence
   - **Step 3**: Suy luận đánh giá phù hợp — multi-step reasoning
   - **Step 4**: Hành động thực tế (đặt lịch + gửi thông báo) — tool interaction + side effects

3. **Guardrail hoạt động tốt**: Agent dừng đúng sau 4 steps (≤ MAX_ITERATIONS), không bị lặp vô hạn.

4. **Kết luận**: Bài toán sàng lọc hồ sơ tuyển dụng & hẹn phỏng vấn **RẤT CẦN ReAct Agent**. Chi phí orchestration hoàn toàn xứng đáng vì Agent giải quyết được toàn bộ quy trình mà Chatbot không thể.
