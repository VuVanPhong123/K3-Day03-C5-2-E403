import copy
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from app import execute_tool, parse_agent_response, run_baseline_chatbot, run_react_agent
from mock_data import BOOKED_INTERVIEWS, CANDIDATES_DB, INTERVIEW_SCHEDULE, JOBS_DB
from prompts import MAX_ITERATIONS
from providers import MockProvider
from tools import AVAILABLE_TOOLS, schedule_interview


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.provider = MockProvider()
        self.bookings = copy.deepcopy(BOOKED_INTERVIEWS)

    def test_parse_valid_one_arg_action(self):
        parsed = parse_agent_response('Thought: Need profile.\nAction: get_candidate_profile["CV_001"]')
        self.assertEqual(parsed["type"], "action")
        self.assertEqual(parsed["tool_name"], "get_candidate_profile")
        self.assertEqual(parsed["args"], ["CV_001"])

    def test_parse_valid_multi_arg_action(self):
        parsed = parse_agent_response(
            'Thought: Book it.\nAction: schedule_interview["CV_001", "2026-08-05", "09:00", "backend_senior", true]'
        )
        self.assertEqual(parsed["type"], "action")
        self.assertEqual(parsed["tool_name"], "schedule_interview")
        self.assertEqual(parsed["args"], ["CV_001", "2026-08-05", "09:00", "backend_senior", True])

    def test_parse_final_answer(self):
        parsed = parse_agent_response("Thought: Done.\nFinal Answer: Safe answer.")
        self.assertEqual(parsed["type"], "final")
        self.assertEqual(parsed["final_answer"], "Safe answer.")

    def test_malformed_action_no_crash(self):
        parsed = parse_agent_response("Thought: Bad.\nAction: get_candidate_profile[CV_001")
        self.assertEqual(parsed["type"], "error")
        self.assertEqual(parsed["code"], "MALFORMED_ACTION")

    def test_unknown_tool_returns_observation_error(self):
        result = execute_tool(
            "missing_tool",
            ["CV_001"],
            candidates_db=CANDIDATES_DB,
            jobs_db=JOBS_DB,
            interview_schedule=INTERVIEW_SCHEDULE,
            booked_interviews=self.bookings,
        )
        payload = json.loads(result)
        self.assertTrue(payload["error"])
        self.assertEqual(payload["code"], "UNKNOWN_TOOL")

    def test_tool_registry_schema_matches_required_args(self):
        self.assertEqual(
            AVAILABLE_TOOLS["schedule_interview"]["parameters"]["required"],
            ["candidate_id", "date", "time", "job_id", "confirmed"],
        )
        self.assertEqual(
            AVAILABLE_TOOLS["send_notification"]["parameters"]["required"],
            ["candidate_id", "notification_type"],
        )

    def test_invalid_date_no_booking(self):
        before = len(self.bookings)
        result = schedule_interview(
            "CV_001",
            "2026-02-31",
            "09:00",
            "backend_senior",
            True,
            CANDIDATES_DB,
            INTERVIEW_SCHEDULE,
            self.bookings,
        )
        payload = json.loads(result)
        self.assertTrue(payload["error"])
        self.assertEqual(payload["code"], "INVALID_DATE")
        self.assertEqual(len(self.bookings), before)

    def test_schedule_without_confirmation_no_booking(self):
        before = len(self.bookings)
        result = schedule_interview(
            "CV_001",
            "2026-08-05",
            "09:00",
            "backend_senior",
            False,
            CANDIDATES_DB,
            INTERVIEW_SCHEDULE,
            self.bookings,
        )
        payload = json.loads(result)
        self.assertTrue(payload["error"])
        self.assertEqual(payload["code"], "NEED_CONFIRMATION")
        self.assertEqual(len(self.bookings), before)

    def test_schedule_with_confirmation_creates_booking(self):
        before = len(self.bookings)
        result = schedule_interview(
            "CV_001",
            "2026-08-05",
            "09:00",
            "backend_senior",
            True,
            CANDIDATES_DB,
            INTERVIEW_SCHEDULE,
            self.bookings,
        )
        payload = json.loads(result)
        self.assertFalse(payload["error"])
        self.assertEqual(len(self.bookings), before + 1)

    def test_repeated_action_not_executed_twice(self):
        result = run_react_agent(
            "[TEST_REPEATED_ACTION] Hãy lấy hồ sơ CV_001 nhưng đừng lặp vô hạn.",
            self.provider,
            verbose=False,
        )
        observations = [step.get("observation", "") for step in result["steps"]]
        self.assertTrue(any("REPEATED_ACTION" in observation for observation in observations))
        executed_profile_calls = [
            step
            for step in result["steps"]
            if step.get("tool_name") == "get_candidate_profile" and step.get("executed") is True
        ]
        self.assertEqual(len(executed_profile_calls), 1)
        self.assertEqual(result["tool_calls"], 1)

    def test_max_iterations_safe_fallback(self):
        result = run_react_agent(
            "[TEST_MAX_ITERATIONS] Hãy tiếp tục sinh lỗi để kiểm tra guardrail.",
            self.provider,
            verbose=False,
        )
        self.assertEqual(result["terminated_by"], "max_iterations")
        self.assertEqual(len(result["steps"]), MAX_ITERATIONS)

    def test_core_multi_tool_does_not_schedule(self):
        question = (
            "Hãy đối chiếu CV_001 với vị trí backend_senior, chỉ ra kỹ năng đã khớp và còn thiếu, "
            "sau đó kiểm tra các slot phỏng vấn còn trống ngày 2026-08-05. Chưa đặt lịch."
        )
        before = len(self.bookings)
        result = run_react_agent(question, self.provider, booked_interviews=self.bookings, verbose=False)
        self.assertEqual(len(self.bookings), before)
        self.assertFalse(any(step.get("tool_name") == "schedule_interview" for step in result["steps"]))
        self.assertIn("chưa đặt lịch", result["final_answer"].lower())

    def test_agent_does_not_schedule_when_user_says_not_confirmed(self):
        question = "Đặt lịch phỏng vấn CV_001 ngày 2026-08-05 lúc 09:00 cho backend_senior nhưng chưa xác nhận."
        before = len(self.bookings)
        result = run_react_agent(question, self.provider, booked_interviews=self.bookings, verbose=False)
        self.assertEqual(len(self.bookings), before)
        self.assertFalse(any(step.get("tool_name") == "schedule_interview" for step in result["steps"]))
        self.assertIn("chưa đặt lịch", result["final_answer"].lower())

    def test_core_evaluation_same_question_baseline_and_agent(self):
        question = "CV_001 có bao nhiêu năm kinh nghiệm và có những kỹ năng nào?"
        baseline = run_baseline_chatbot(question, self.provider, verbose=False)
        agent = run_react_agent(question, self.provider, verbose=False)
        self.assertEqual(baseline["question"], agent["question"])
        self.assertEqual(baseline["tool_calls"], 0)
        self.assertGreaterEqual(agent["tool_calls"], 1)

    def test_mock_provider_react_path_calls_provider_through_true_loop(self):
        result = run_react_agent(
            "CV_001 có bao nhiêu năm kinh nghiệm và có những kỹ năng nào?",
            self.provider,
            verbose=False,
        )
        self.assertGreaterEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][0]["tool_name"], "get_candidate_profile")
        self.assertEqual(result["terminated_by"], "final_answer")


if __name__ == "__main__":
    unittest.main()
