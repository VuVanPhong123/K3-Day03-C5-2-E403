# Nhóm C5-2

| Thành viên | MSSV |
| :-- | :-- |
| Phạm Sỹ Đức | 2A202601601 |
| Hoàng Lê Minh | 2A202601653 |
| Hà Duy Anh | 2A202601511 |
| Nguyễn Quang Vinh | 2A202601517 |
| Đoàn Nhật Nam | 2A202601123 |
| Vũ Văn Phong | 2A202601647 |

## Đề tài

**Chủ đề 9:** Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn.

Lab so sánh hai hướng:
- **Baseline Chatbot:** chỉ dùng LLM trả lời, không gọi tool, không truy cập dữ liệu nội bộ.
- **ReAct Agent:** chạy vòng lặp `Thought -> Action -> Observation -> Final Answer`, parse Action từ LLM/provider, gọi tool trong registry và áp dụng guardrails.

## Chức năng chính

- Tra cứu hồ sơ ứng viên: `get_candidate_profile`
- Tra cứu JD/vị trí tuyển dụng: `get_job_requirements`
- Đối chiếu CV với JD bằng tín hiệu trung lập: `evaluate_fit`
- Kiểm tra slot phỏng vấn còn trống: `check_interview_schedule`
- Đặt lịch phỏng vấn mock/in-memory sau khi có xác nhận: `schedule_interview`
- Tạo thông báo mock, không gửi email thật: `send_notification`
- Tra cứu trạng thái phỏng vấn: `get_interview_status`

## Cách chạy thủ công

Tạo môi trường và cài thư viện nếu cần:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Chạy offline bằng mock provider:

```bash
$env:LLM_PROVIDER="mock"
python src\app.py
python src\app.py --mode core-tests
python src\app.py --mode cross-audit
```

Chạy với Gemini nếu `.env` đã có `GEMINI_API_KEY` và model:

```bash
$env:LLM_PROVIDER="gemini"
$env:LLM_MODEL="gemini-3.1-flash-lite"
python src\app.py --mode core-tests
```

## Các mode CLI

- `demo`: chạy một câu baseline và một câu ReAct multi-tool.
- `core-tests`: chạy 5 acceptance questions trong `config/test_cases.json` qua cả baseline và agent.
- `cross-audit`: chạy các probe guardrail như malformed action, unknown tool, repeated action, max iterations và confirmation gate.

## Kiểm thử

```bash
python -m compileall src tests
python -m unittest discover -s tests -v
```

## Artifact nộp bài

- `src/app.py`: ReAct loop, parser, executor, CLI.
- `src/tools.py`: pure tools + registry schema.
- `src/prompts.py`: baseline prompt, ReAct protocol, guardrails.
- `src/providers.py`: multi-provider adapter + `MockProvider` offline.
- `config/test_cases.json`: 5 core tests và extended guardrail tests.
- `tests/test_agent.py`: unit tests không gọi network.
- `docs/trace_eval.md`: scoring, trace, RCA, cross-audit.
- `docs/hybrid_flowchart.mermaid`: sơ đồ hybrid chatbot/agent.
- `docs/PHAN_CONG_CONG_VIEC.md`: phân công vai trò nhóm.
