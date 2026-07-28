"""
Core demo app for Lab 03.

Current topic: Recruitment Assistant Agent.
Phase 2 shows a baseline chatbot path.
Phase 3 shows a deterministic ReAct-style path using the implemented tools.
"""

import copy
import json
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mock_data import BOOKED_INTERVIEWS, CANDIDATES_DB, INTERVIEW_SCHEDULE, JOBS_DB
from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider
from tools import (
    AVAILABLE_TOOLS,
    check_interview_schedule,
    evaluate_fit,
    get_candidate_profile,
    get_job_requirements,
    schedule_interview,
    send_notification,
)

load_dotenv()


def load_test_cases():
    """Load Role 1 test cases from config/test_cases.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """Run one baseline LLM generation without tools."""
    print(f"\n[CHATBOT BASELINE] User query: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"[Baseline Answer]\n{response}")
    return response


def run_react_agent(user_query: str, provider=None):
    """
    Run a small deterministic Phase 3 ReAct demo.

    This is intentionally simple for the lab demo: it uses the real recruitment
    tools and mock data, but does not yet implement an LLM action parser.
    """
    booked_interviews = copy.deepcopy(BOOKED_INTERVIEWS)
    candidate_id = "CV_001"
    job_id = "backend_senior"
    interview_date = "2026-08-05"
    interview_time = "09:00"

    print(f"\n[REACT AGENT] User query: {user_query}")
    print(f"Available tools: {', '.join(AVAILABLE_TOOLS.keys())}")

    step = 1
    print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
    print("Thought: Need the candidate profile before screening.")
    print(f"Action: get_candidate_profile[{candidate_id}]")
    observation = get_candidate_profile(candidate_id, CANDIDATES_DB)
    print(f"Observation:\n{observation}")

    step += 1
    print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
    print("Thought: Need the job requirements to compare against the CV.")
    print(f"Action: get_job_requirements[{job_id}]")
    observation = get_job_requirements(job_id, JOBS_DB)
    print(f"Observation:\n{observation}")

    step += 1
    print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
    print("Thought: Candidate and job data are available, so evaluate fit.")
    print(f"Action: evaluate_fit[{candidate_id}, {job_id}]")
    fit_observation = evaluate_fit(candidate_id, job_id, CANDIDATES_DB, JOBS_DB)
    print(f"Observation:\n{fit_observation}")

    step += 1
    print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
    print("Thought: Fit is strong enough for a demo interview scheduling step.")
    print(f"Action: check_interview_schedule[{interview_date}]")
    schedule_observation = check_interview_schedule(
        interview_date,
        INTERVIEW_SCHEDULE,
        booked_interviews,
    )
    print(f"Observation:\n{schedule_observation}")

    print(f"Action: schedule_interview[{candidate_id}, {interview_date}, {interview_time}, {job_id}]")
    booking_observation = schedule_interview(
        candidate_id,
        interview_date,
        interview_time,
        job_id,
        CANDIDATES_DB,
        INTERVIEW_SCHEDULE,
        booked_interviews,
    )
    print(f"Observation:\n{booking_observation}")

    print(f"Action: send_notification[{candidate_id}, interview_scheduled]")
    notification_observation = send_notification(
        candidate_id,
        "interview_scheduled",
        CANDIDATES_DB,
        booked_interviews,
    )
    print(f"Observation:\n{notification_observation}")

    print("\nThought: I have candidate data, job data, fit evidence, schedule availability, booking confirmation, and notification status.")
    print(
        "Final Answer: CV_001 is a strong match for backend_senior. "
        "The demo scheduled an interview on 2026-08-05 at 09:00 and generated a notification confirmation."
    )


if __name__ == "__main__":
    print("=" * 58)
    print("VINUNI LAB 03 - CHATBOT VS REACT AGENT")
    print("=" * 58)

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"LLM Provider: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"Loaded {len(tests)} test cases from config/test_cases.json")

    baseline_query = tests[1]["question"] if len(tests) > 1 else "CV cua Nguyen Van A co bao nhieu nam kinh nghiem?"
    react_query = "Danh gia CV_001 cho vi tri backend_senior va demo dat lich phong van."

    print("\n--- DEMO 1: PHASE 2 BASELINE CHATBOT ---")
    run_baseline_chatbot(baseline_query, provider)

    print("\n--- DEMO 2: PHASE 3 REACT AGENT ---")
    run_react_agent(react_query, provider)
