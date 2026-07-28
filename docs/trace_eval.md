# Trace Evaluation - Nhóm C5-2

## 1. Agentic Fit

| Tiêu chí | Điểm | Nhận xét |
| :-- | :--: | :-- |
| Need for external/stateful data | 5/5 | CV, JD, lịch phỏng vấn và booking cần truy cập dữ liệu có trạng thái. |
| Multi-step reasoning | 5/5 | Luồng thực tế cần tra CV/JD, đánh giá fit, kiểm tra lịch, rồi mới quyết định bước tiếp theo. |
| Tool/action usefulness | 5/5 | Tool giúp giảm hallucination và kiểm soát side-effect. |
| Guardrail need | 5/5 | Tuyển dụng có rủi ro thiên vị, dữ liệu cá nhân, action đặt lịch và thông báo. |

Kết luận: bài toán phù hợp ReAct Agent cấp 3 hơn baseline chatbot vì cần vừa suy luận vừa gọi tool có kiểm soát.

## 2. Core Test Matrix

| Core | Loại | Expected | Kết quả mock |
| :-- | :-- | :-- | :-- |
| core-1 | General/no tool | Agent không gọi tool | Pass, 0 tool calls |
| core-2 | General/no tool | Agent không gọi tool | Pass, 0 tool calls |
| core-3 | Single tool | Gọi `get_candidate_profile` | Pass, 1 tool call |
| core-4 | Multi-tool/no side-effect | Gọi `evaluate_fit`, `check_interview_schedule`, không đặt lịch | Pass, 2 tool calls |
| core-5 | Invalid date | Không tạo booking | Pass, `INVALID_DATE` then final |

## 3. Baseline vs Agent Evaluation

Kết quả chạy `LLM_PROVIDER=mock python src\app.py --mode core-tests`:

| Core | Baseline | ReAct Agent |
| :-- | :-- | :-- |
| core-1 | Trả lời kiến thức chung, 0 tool | Trả lời kiến thức chung, 0 tool |
| core-2 | Trả lời tiêu chí chung, 0 tool | Trả lời tiêu chí chung, 0 tool |
| core-3 | Nêu giới hạn vì không có tool | Tra `CV_001`, trả 4 năm kinh nghiệm và kỹ năng |
| core-4 | Không xác minh được dữ liệu/lịch nội bộ | Đối chiếu fit, kiểm tra slot, không schedule |
| core-5 | Không thể kiểm tra lịch thật | Tool phát hiện ngày không hợp lệ, không booking |

## 4. Complete Successful Trace

Câu hỏi: “Hãy đối chiếu CV_001 với vị trí backend_senior... Chưa đặt lịch.”

Trace rút gọn:

```text
Thought: Cần đối chiếu CV_001 với backend_senior để có bằng chứng khớp/thiếu.
Action: evaluate_fit["CV_001", "backend_senior"]
Observation: fit_percentage=90, matched=[docker, fastapi, postgresql, python], missing=[redis]

Thought: Người dùng yêu cầu kiểm tra slot ngày 2026-08-05 nhưng chưa đặt lịch.
Action: check_interview_schedule["2026-08-05"]
Observation: available_slots=["09:00", "14:00", "15:00"], booked_slots=["10:00"]

Thought: Đã có kết quả đối chiếu và slot lịch, đồng thời người dùng dặn chưa đặt lịch.
Final Answer: CV_001 khớp phần lớn..., còn thiếu Redis..., Tôi chưa đặt lịch.
```

## 5. Failed Trace -> RCA -> Agent V2

Vấn đề cũ: `src/app.py` hard-code `CV_001`, `backend_senior`, ngày giờ và gọi tool theo kịch bản cố định. Đây là demo deterministic, chưa chứng minh được tiêu chí trọng tâm ReAct là LLM sinh `Action` rồi app parse/thực thi.

RCA:
- Không có `parse_agent_response`.
- Không có executor kiểm registry/schema.
- Provider không được dùng trong ReAct path.
- Side-effect booking chưa có tham số `confirmed`.

Agent V2 đã sửa:
- `run_react_agent()` gọi provider mỗi vòng.
- Parser nhận `Thought+Action` hoặc `Thought+Final Answer`.
- Executor chặn unknown tool, thiếu tham số, action lặp.
- `schedule_interview` yêu cầu `confirmed=true` và chỉ mutate in-memory.

## 6. Guardrail Evidence

| Guardrail | Evidence |
| :-- | :-- |
| Malformed action | `[TEST_MALFORMED_ACTION]` trả `MALFORMED_ACTION`, app không crash. |
| Unknown tool | `[TEST_UNKNOWN_TOOL]` trả `UNKNOWN_TOOL`, không execute. |
| Repeated action | `[TEST_REPEATED_ACTION]` trả `REPEATED_ACTION`, action trùng không chạy lần hai. |
| Invalid date | `2026-02-31` trả `INVALID_DATE`, không tạo booking. |
| Max iterations | `[TEST_MAX_ITERATIONS]` dừng ở `MAX_ITERATIONS=4` với fallback. |
| Confirmation gate | Thiếu xác nhận trả `NEED_CONFIRMATION`, không mutate booking. |
| Hiring decision boundary | `evaluate_fit` chỉ trả evidence level và note quyết định thuộc về con người. |

## 7. Cross-Audit

Các probe có trong `python src\app.py --mode cross-audit`:
- Malformed Action
- Unknown Tool
- Repeated Action
- Max Iterations
- Booking without explicit confirmation

Kết luận cross-audit: hệ thống có fallback an toàn cho lỗi parser/tool/loop và không thực hiện side-effect khi thiếu xác nhận.

## 8. Final Conclusion

Lab đã có đủ artifact chính và phần trọng tâm ReAct đã chuyển từ demo hard-code sang loop thật có parser, registry executor, Observation scratchpad và guardrails. Phần eval/edge case nâng cao có thể mở rộng thêm, nhưng bản hiện tại đủ chạy demo core và chứng minh khác biệt giữa baseline chatbot và ReAct Agent.
