# Phân Công Công Việc - Nhóm C5-2

## Bảng Phân Vai

| Vai trò | File đảm nhận | Nhiệm vụ chính | Người đảm nhận |
| :-- | :-- | :-- | :-- |
| Role 1: Product Architect | `config/test_cases.json` | Định hướng bài toán, chuẩn hóa core/extended test cases | Hà Duy Anh |
| Role 2: Tool Engineer | `src/tools.py` | Thiết kế tool, schema, validation, confirmation gate | Nguyễn Quang Vinh |
| Role 3: Prompt Engineer | `src/prompts.py` | Baseline prompt, ReAct protocol, guardrails | Hoàng Lê Minh |
| Role 4: Core Developer / Integrator | `src/app.py` | Parser, ReAct loop, executor, CLI tích hợp | Đoàn Nhật Nam |
| Role 5A: Trace Analyst / QA | `docs/trace_eval.md`, `tests/test_agent.py` | Trace, RCA, acceptance tests, báo cáo | Phạm Sỹ Đức |
| Role 5B: Flowchart Architect | `docs/hybrid_flowchart.mermaid`, cross-audit | Hybrid flowchart, edge flow, demo evidence | Vũ Văn Phong |

## Checklist Hoàn Thành

- [x] Chọn đề tài: Chủ đề 9 - Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn.
- [x] Có baseline chatbot không gọi tool.
- [x] Có tool registry với schema rõ ràng.
- [x] Có ReAct prompt ép format `Thought -> Action -> Observation -> Final Answer`.
- [x] Có ReAct loop thật trong `src/app.py`, parse Action từ provider và gọi tool qua registry.
- [x] Có confirmation gate cho `schedule_interview`.
- [x] Có guardrail cho malformed action, unknown tool, repeated action, invalid date và max iterations.
- [x] Có 5 core acceptance tests trong `config/test_cases.json`.
- [x] Có unit tests trong `tests/test_agent.py`.
- [x] Có trace/evaluation report trong `docs/trace_eval.md`.
- [x] Có hybrid flowchart trong `docs/hybrid_flowchart.mermaid`.

## Quy Trình Chạy Demo

```bash
$env:LLM_PROVIDER="mock"
python src\app.py --mode demo
python src\app.py --mode core-tests
python src\app.py --mode cross-audit
python -m unittest discover -s tests -v
```

## Ghi Chú An Toàn

- Không có side-effect thật: lịch và notification chỉ là mock/in-memory.
- Không sửa `.env`, không commit API key.
- Không tự động gửi rejection notification; prompt yêu cầu HR xử lý/xác nhận thủ công.
- Tool `evaluate_fit` chỉ trả tín hiệu sàng lọc, không ra quyết định tuyển dụng cuối cùng.
