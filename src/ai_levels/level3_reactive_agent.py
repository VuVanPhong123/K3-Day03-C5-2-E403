"""
Level 3: Reactive Agent / ReAct Demo.

This demo delegates to the real ReAct loop in src/app.py so it parses Action
from the provider instead of running a hard-coded script.
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

from app import run_react_agent
from providers import MockProvider


def reactive_agent_step(user_goal: str) -> None:
    result = run_react_agent(user_goal, MockProvider(), verbose=True)
    print(f"\nTerminated by: {result['terminated_by']}")
    print(f"Tool calls: {result['tool_calls']}")


if __name__ == "__main__":
    print("=== DEMO LEVEL 3: REACTIVE AGENT ===")
    reactive_agent_step(
        "Hãy đối chiếu CV_001 với vị trí backend_senior, sau đó kiểm tra các slot phỏng vấn "
        "còn trống ngày 2026-08-05. Chưa đặt lịch."
    )
