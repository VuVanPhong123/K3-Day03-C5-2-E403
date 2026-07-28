"""
Level 3: Reactive Agent / ReAct Demo.

Runs Thought -> Action -> Observation with the real recruitment tools.
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

from mock_data import CANDIDATES_DB, JOBS_DB
from tools import evaluate_fit, get_candidate_profile, get_job_requirements


def reactive_agent_step(user_goal: str) -> None:
    candidate_id = "CV_001"
    job_id = "backend_senior"

    print(f"Goal: {user_goal}")

    print("\nThought 1: Need candidate evidence.")
    print(f"Action 1 : get_candidate_profile[{candidate_id}]")
    obs1 = get_candidate_profile(candidate_id, CANDIDATES_DB)
    print(f"Observation 1:\n{obs1}")

    print("\nThought 2: Need job requirements.")
    print(f"Action 2 : get_job_requirements[{job_id}]")
    obs2 = get_job_requirements(job_id, JOBS_DB)
    print(f"Observation 2:\n{obs2}")

    print("\nThought 3: Compare candidate evidence with the JD.")
    print(f"Action 3 : evaluate_fit[{candidate_id}, {job_id}]")
    obs3 = evaluate_fit(candidate_id, job_id, CANDIDATES_DB, JOBS_DB)
    print(f"Observation 3:\n{obs3}")

    print("\nFinal Answer: CV_001 is evaluated against backend_senior using tool observations above.")


if __name__ == "__main__":
    print("=== DEMO LEVEL 3: REACTIVE AGENT ===")
    reactive_agent_step("Evaluate CV_001 for backend_senior.")
