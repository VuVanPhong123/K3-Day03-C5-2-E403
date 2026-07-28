"""
Level 4: Autonomous Agent Demo.

Shows planning and memory on top of the recruitment workflow.
This is a conceptual demo, not a full autonomous production agent.
"""

import os
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from mock_data import BOOKED_INTERVIEWS, CANDIDATES_DB, INTERVIEW_SCHEDULE, JOBS_DB
from tools import check_interview_schedule, evaluate_fit, schedule_interview


class AutonomousGoalAgent:
    def __init__(self, goal: str, max_steps: int = 4):
        self.goal = goal
        self.max_steps = max_steps
        self.memory = []

    def remember(self, step: int, plan: str, result: str) -> None:
        self.memory.append({"step": step, "plan": plan, "result": result})

    def execute(self) -> None:
        print(f"=== AUTONOMOUS GOAL: {self.goal} ===")

        candidate_id = "CV_001"
        job_id = "backend_senior"
        date = "2026-08-05"
        time = "09:00"
        booked = dict(BOOKED_INTERVIEWS)

        print(f"\n--- Planning Step 1/{self.max_steps} ---")
        plan = "Evaluate candidate fit."
        result = evaluate_fit(candidate_id, job_id, CANDIDATES_DB, JOBS_DB)
        self.remember(1, plan, result)
        print(f"Plan  : {plan}")
        print(f"Result:\n{result}")

        print(f"\n--- Planning Step 2/{self.max_steps} ---")
        plan = "Check interview availability."
        result = check_interview_schedule(date, INTERVIEW_SCHEDULE, booked)
        self.remember(2, plan, result)
        print(f"Plan  : {plan}")
        print(f"Result:\n{result}")

        print(f"\n--- Planning Step 3/{self.max_steps} ---")
        plan = "Schedule interview for the selected slot after explicit demo confirmation."
        result = schedule_interview(candidate_id, date, time, job_id, True, CANDIDATES_DB, INTERVIEW_SCHEDULE, booked)
        self.remember(3, plan, result)
        print(f"Plan  : {plan}")
        print(f"Result:\n{result}")

        print(f"\n--- Evaluation Step 4/{self.max_steps} ---")
        print(f"Memory entries: {len(self.memory)}")
        print("Goal evaluation: demo workflow completed.")


if __name__ == "__main__":
    agent = AutonomousGoalAgent("Screen CV_001 and schedule a demo interview.")
    agent.execute()
